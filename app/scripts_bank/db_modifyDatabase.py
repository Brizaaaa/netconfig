from app import app, db, models
from sqlalchemy import asc, func
from lib.ip_functions import validateIPAddress
from lib.functions import stripNewline
import netboxAPI
from ..device_classes import deviceType as dt


def addHostToDB(hostname, ipv4_addr, type, ios_type):
    """Add host to database.  Returns True if successful."""
    try:
        host = models.Host(hostname=hostname, ipv4_addr=ipv4_addr, type=type, ios_type=ios_type)
        db.session.add(host)
        # This enables pulling ID for newly inserted host
        db.session.flush()
        db.session.commit()
        return True, host.id
    except:
        return False, 0


def importHostsToDB(csvImport):
    """Import hosts to database.

    Returns True if successful
    Format: Hostname,IPAddress,DeviceType,IOSType
    """
    # For each line in csvImport, run validation checks
    for x in csvImport.split('\n'):
        if x:
            # Split array by comma's
            xArray = x.split(',')
            # 0 is hostname, 1 is IP address, 2 is device type, 3 is ios type
            if not validateIPAddress(xArray[1]):
                return False, "Invalid IP address for host %s - value entered: %s" % (xArray[0], xArray[1])

            if xArray[2].lower() not in ("switch", "router", "firewall"):
                return False, "Invalid device type for host %s - value entered: %s" % (xArray[0], xArray[2])

            if stripNewline(xArray[3].lower()) not in ("ios", "ios-xe", "nx-os", "asa"):
                return False, "Invalid IOS type for host %s - value entered: %s" % (xArray[0], xArray[3])

    # Each line has been validated, so import all lines into DB
    for x in csvImport.split('\n'):
        if x:
            # Split array by comma's
            xArray = x.split(',')
            # 0 is hostname, 1 is IP address, 2 is device type, 3 is ios type
            hostname = xArray[0]
            ipv4_addr = xArray[1]

            if xArray[2].lower() == 'switch':
                type = "Switch"
            elif xArray[2].lower() == 'router':
                type = "Router"
            elif xArray[2].lower() == 'firewall':
                type = "Firewall"
            else:
                type = "Error"

            if stripNewline(xArray[3].lower()) == 'ios':
                ios_type = "cisco_ios"
            elif stripNewline(xArray[3].lower()) == 'ios-xe':
                ios_type = "cisco_xe"
            elif stripNewline(xArray[3].lower()) == 'nx-os':
                ios_type = "cisco_nxos"
            elif stripNewline(xArray[3].lower()) == 'asa':
                ios_type = "cisco_asa"
            else:
                ios_type = "Error"

            try:
                host = models.Host(hostname=hostname, ipv4_addr=ipv4_addr, type=type, ios_type=ios_type)
                db.session.add(host)
                # This enables pulling ID for newly inserted host
                db.session.flush()
                db.session.commit()
            except:
                return False, "Error during import of devices into database"

    return True, "Successfully added all %s devices" % (len(csvImport))


def deleteHostInDB(x):
    """Remove host from database.

    Returns True if successful.
    x is the host ID
    """
    try:
        host = models.Host.query.filter_by(id=x).first()
        db.session.delete(host)
        db.session.commit()
        return True
    except:
        return False


def getHosts(page):
    """Get certain number of devices in database."""
    hosts = models.Host.query.order_by(asc(models.Host.hostname)).paginate(page, app.config['POSTS_PER_PAGE'], False)
    return hosts


def getHostsAll():
    """Get all devices in database."""
    hosts = models.Host.query.all()
    return hosts


def getHostByHostname(x):
    """Get device in database by hostname."""
    host = models.Host.query.filter(func.lower(models.Host.hostname) == func.lower(x)).first()  # <-- not case sensitve
    return host


def getHostIDbyHostname(x):
    """Get device ID in database by hostname."""
    host = models.Host.query.filter_by(hostname=x).first()
    return host.id


def getHostByID(x):
    """Get device by ID.

    Support local database or Netbox inventory.
    """
    if app.config['DATALOCATION'] == 'local':
        host = models.Host.query.filter_by(id=x).first()
    elif app.config['DATALOCATION'] == 'netbox':
        host = netboxAPI.getHostByID(x)

    # Get host class based on device type
    return dt.DeviceHandler(id=host.id, hostname=host.hostname, ipv4_addr=host.ipv4_addr, type=host.type, ios_type=host.ios_type)


def getHostsByIOSType(x):
    """Get devices by IOS type."""
    hosts = models.Host.query.filter_by(ios_type=x)
    return hosts


def editHostInDatabase(originalHostID, hostname, ipv4_addr, hosttype, ios_type):
    """Edit device in database.

    This is only supported when using the local database.
    """
    if app.config['DATALOCATION'] == 'local':
        try:
            host = models.Host.query.filter_by(id=originalHostID).first()
            if hostname:
                host.hostname = hostname
            if ipv4_addr:
                host.ipv4_addr = ipv4_addr
            if hosttype:
                host.type = hosttype
            if ios_type:
                host.ios_type = ios_type
            db.session.commit()
            return True
        except:
            return False
    else:
        return False


def searchHostInDB(x):
    """Determine if provided IP address is in database.

    Return True if provided host IP address is in database.
    False if it is not.
    Also returns hostname of device.
    """
    try:
        host = models.Host.query.filter_by(ipv4_addr=x).first()
        if host:
            return True, host.hostname
        else:
            return False, ''
    except:
        return False, ''
