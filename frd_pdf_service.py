from http.server import BaseHTTPRequestHandler, HTTPServer
import io, textwrap, os

LINES=[
'PUBLIC RESEARCH OVERVIEW',
'Frontier Research Department (FRD)',
'Independent research and systems development for defensible decisions under changing evidence, authority, and time.',
'',
'MISSION',
'FRD develops and evaluates systems that determine whether available evidence legitimately supports a decision or state change, preserve what was known and justified at the time, and prevent later information from silently rewriting earlier decision context.',
'',
'RESEARCH DOMAINS',
'Evidentiary provenance and integrity; Decision assurance and authority boundaries; Temporal integrity and historical reconstruction; Uncertainty, contradiction, and revocation handling; Adversarial and counterfactual evaluation; Trustworthy automated and agentic decision systems.',
'',
'SYSTEMS IN DEVELOPMENT',
'EPM - provenance, state, and temporal integrity; TVC - temporal and counterfactual research; Governor - admissibility and authority boundaries; Variant Hunter - adversarial testing and edge discovery; FAP-Core - applied decision-assurance workflows.',
'',
'PUBLIC-SAFE PRINCIPLES',
'Claims should not exceed the evidence, provenance, authority, and boundaries supporting them. Later knowledge must not be laundered into earlier decision context. Missing evidence, explicit revocation, and invalid authority are distinct states and should remain distinguishable. Auditability requires preserving both the decision and the conditions that made it justified or unjustified at that time.',
'',
'CURRENT VALIDATION AND BENCHMARK WORK',
'Public synthetic benchmarks exercise valid approval, required deferral, explicit revocation after approval, and reconstruction of earlier justification. Evaluation considers both unsafe approvals and unnecessary blocking. Where independent verification has not occurred, FRD does not claim it.',
'',
'PUBLIC SYSTEMS MAP',
'Evidence -> Verification -> Decision Assurance -> Counterfactual Analysis -> Audit / Reconstruction',
'EPM preserves provenance, state context, temporal integrity, uncertainty, and auditable history. Governor constrains admissibility and authority. Variant Hunter attacks assumptions and edge cases. TVC studies temporal and counterfactual relationships. FAP-Core applies decision-assurance concepts to bounded financial and operational workflows.',
'',
'SYN-AUTH-01 - DECISION INTEGRITY ACROSS TIME',
'PAY-AUTH-v1.0: a payment above $1,000 requires a verified approval record bound to the invoice, amount, and an authorized Finance approver. An explicit valid revocation removes present authorization but does not rewrite whether earlier authorization was valid when it existed.',
'T0 - DEFER: invoice and purchase match present; approval absent.',
'T1 - ALLOW: qualifying approval present and current.',
'T2 - DENY: explicit valid revocation present; T1 remains historically valid.',
'',
'EPISTEMIC STATUS',
'Expected behavior is part of the benchmark contract. Independent comparative results, measured performance, and production guarantees are not claimed on this artifact.',
'',
'Patrick I. B. Paslay | Founder, FRD'
]

def esc(s):
    return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')

def build_pdf():
    pages=[]; current=[]
    for line in LINES:
        if not line:
            current.append(''); continue
        for w in (textwrap.wrap(line, 92) or ['']):
            current.append(w)
            if len(current)>=44:
                pages.append(current); current=[]
    if current: pages.append(current)
    objs=[]
    kids=[]; objnum=4
    for _ in pages:
        kids.append(f'{objnum} 0 R'); objnum += 2
    objs.append('<< /Type /Catalog /Pages 2 0 R >>')
    objs.append(f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(pages)} >>')
    objs.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    heads={'PUBLIC RESEARCH OVERVIEW','MISSION','RESEARCH DOMAINS','SYSTEMS IN DEVELOPMENT','PUBLIC-SAFE PRINCIPLES','CURRENT VALIDATION AND BENCHMARK WORK','PUBLIC SYSTEMS MAP','SYN-AUTH-01 - DECISION INTEGRITY ACROSS TIME','EPISTEMIC STATUS'}
    for idx, lines in enumerate(pages):
        page_obj=4+idx*2; content_obj=page_obj+1
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj} 0 R >>')
        content=['BT']; y=744
        for line in lines:
            size=13 if line in heads else 11
            content += [f'/F1 {size} Tf', f'1 0 0 1 72 {y} Tm ({esc(line)}) Tj']
            y -= 15
        content.append('ET')
        stream='\n'.join(content).encode('latin-1','replace')
        objs.append(f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream')
    out=io.BytesIO(); out.write(b'%PDF-1.4\n'); offsets=[0]
    for i,obj in enumerate(objs, start=1):
        offsets.append(out.tell()); out.write(f'{i} 0 obj\n'.encode())
        out.write(obj if isinstance(obj,bytes) else obj.encode('latin-1')); out.write(b'\nendobj\n')
    xref=out.tell(); out.write(f'xref\n0 {len(objs)+1}\n'.encode()); out.write(b'0000000000 65535 f \n')
    for off in offsets[1:]: out.write(f'{off:010d} 00000 n \n'.encode())
    out.write(f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode())
    return out.getvalue()

PDF=build_pdf()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/':
            body=b'FRD Public Media Pack PDF: /FRD_Public_Media_Pack.pdf\n'
            self.send_response(200); self.send_header('Content-Type','text/plain; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        elif self.path=='/FRD_Public_Media_Pack.pdf':
            self.send_response(200); self.send_header('Content-Type','application/pdf'); self.send_header('Content-Disposition','inline; filename="FRD_Public_Media_Pack.pdf"'); self.send_header('Content-Length',str(len(PDF))); self.end_headers(); self.wfile.write(PDF)
        else:
            self.send_response(404); self.end_headers()
    def log_message(self,*args): pass

if __name__=='__main__':
    HTTPServer(('0.0.0.0', int(os.environ.get('PORT','10000'))), H).serve_forever()
