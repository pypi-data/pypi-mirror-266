import httpx
import os
import sys
from typing import Optional, Callable
from hostfact_python_client.utilities import http_build_query

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


class HostFactCall(object):
    def __init__(self, url: str,
                 api_key: str,
                 controller: Optional[str] = None,
                 transport: Optional[Callable] = None,
                 timeout: int = 30,
                 debug: bool = False):
        self.url = url
        self.api_key = api_key
        self.controller = controller
        self.transport = transport
        self.timeout = timeout
        self.debug = debug

    def call(self, **kwargs):
        data = {
            "api_key": self.api_key,
            "controller": self.controller,
            "action": self.name,
            **kwargs
        }
        d = http_build_query(data)
        try:
            if self.transport:
                # Use the provided transport to make the HTTP request
                response = self.transport.request(self.url,
                                                  data=d,
                                                  headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                                  timeout=self.timeout)
            else:
                response = httpx.post(self.url,
                                      data=d,
                                      headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                      timeout=self.timeout)
        except Exception as e:
            if self.debug:
                print(f"HostFact error: {e}")
            raise Exception(f"HostFact error: {e}")
        reply = response.json()

        if response.status_code != 200:
            error = f"HostFact error: {response.text}"
            if self.debug:
                print(error)
            raise Exception(error)

        if reply['status'] == 'error':
            if self.debug:
                print(f"HostFact error: {reply}")
            raise Exception(f"HostFact error: {reply['errors']}" if 'errors' in reply.keys() else Exception("HostFact error."))
        return reply

    def make_invoice(self,
                     debtor_code: str,
                     invoice_lines: list,
                     newInvoice: bool = False,
                     attachment=None):
        method = HostFactCall(self.url, self.api_key, 'invoice', self.debug)

        active_invoices = []

        if not newInvoice:
            active_invoices = method.list(searchat="DebtorCode", searchfor=debtor_code, status=0, sort="Modified")

        if newInvoice or (not newInvoice and active_invoices['totalresults'] == 0):
            invoice_reply = method.add(DebtorCode=debtor_code, InvoiceLines=invoice_lines)
        else:
            invoice_line_method = HostFactCall(self.url, self.api_key, 'invoiceline', self.debug)
            invoice_reply = invoice_line_method.add(Identifier=active_invoices['invoices'][0]['Identifier'], InvoiceLines=invoice_lines)

        if attachment:
            attachment_method = HostFactCall(self.url, self.api_key, 'attachment', self.debug)
            attachment_method.add(InvoiceCode=invoice_reply['invoice']['InvoiceCode'], Type='invoice', Filename=attachment['name'], Base64=attachment['content'])

        return {"Identifier": invoice_reply['invoice']['Identifier']}

    def __getattr__(self, name: str):
        if name == "make_invoice":
            if self.controller == "invoice":
                return self.make_invoice
            else:
                raise Exception("make_invoice only allowed for 'invoice' controller")
        self.name = name
        return self.call


class HostFact(object):
    def __init__(self,
                 url: str,
                 api_key: str,
                 transport: Optional[Callable] = None,
                 timeout: int = 30,
                 debug: bool = False):
        self.url = url
        self.api_key = api_key
        self.method = HostFactCall(self.url, self.api_key, transport=transport, timeout=timeout, debug=debug)

    def __getattr__(self, name):
        setattr(self.method, "controller", name)
        return self.method
