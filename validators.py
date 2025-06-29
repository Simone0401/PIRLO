import re
import ipaddress
from wtforms.validators import ValidationError

# regex semplificata per hostname (RFC 1123)
HOSTNAME_REGEX = re.compile(
    r'^(?=.{1,253}$)(?!-)[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.?$'
)

def IPOrHostname():
    message = 'Deve essere un indirizzo IP valido o un nome di dominio (es. example.com).'

    def _ip_or_host(form, field):
        v = field.data.strip()
        # prova IP
        try:
            ipaddress.ip_address(v)
            return
        except ValueError:
            pass
        # prova hostname
        if not HOSTNAME_REGEX.match(v):
            raise ValidationError(message)

    return _ip_or_host
