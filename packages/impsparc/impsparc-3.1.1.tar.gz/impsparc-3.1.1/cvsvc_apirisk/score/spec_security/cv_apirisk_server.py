import os
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
import requests

from sanic import Sanic
from sanic.response import json as sjson

from cvsvc_apirisk.score.spec_security.cv_apirisk_assessment import \
                            generate_report_spec


app = Sanic(__name__)


@app.route('/eval_risk', methods=['POST'])
def eval_risk(request):

    spec_url = request.json['spec_url']
    cv_rules_path = request.json['cv_rules_path']
    custom_rules_path = request.json['custom_rules_path']

    if spec_url.startswith('file://'):
        spec_path = spec_url[7:]
    else:
        rsp = requests.get(spec_url)
        spec_filename = spec_url.split('/')[-1]
        spec_path = '%s/%s' % (app.cvroot, spec_filename)
        with open(spec_path, 'w') as outf:
            outf.write(rsp.text)

    report = generate_report_spec(spec_path, None, cv_rules_path,
                                  custom_rules_path)

    return sjson(report)


def main(argv=sys.argv):
    apar = ArgumentParser()
    apar.add_argument('-c', dest='cfg_file')
    args = apar.parse_args()

    cpar = ConfigParser()
    cpar.read(args.cfg_file)

    host = cpar.get('Server', 'host')
    port = cpar.getint('Server', 'port')
    app.cvroot = cpar.get('ApiSparc', 'cvroot')

    try:
        os.mkdir(app.cvroot)
    except FileExistsError:
        pass
    except:
        raise

    app.run(host=host, port=port)

    return


if __name__ == '__main__':
    sys.exit(main())
