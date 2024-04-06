from secvision import get_agent_version, get_proxy_version

USAGE = "version"
ABOUT = "Show version information about the SecVision Python Agent"


def command(options, args):
    print('Agent version: v%s' % get_agent_version())
    print('Proxy version: v%s' % get_proxy_version())
