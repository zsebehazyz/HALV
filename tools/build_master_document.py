#!/usr/bin/env python3
"""Build the user's complete, continuously refreshed MD from saved research.

Embeds the full journal, hypothesis map, all detailed reports and model JSONs.
Large evidence/program files stay linked with hashes. In append-only mode,
validate the existing document and update its manifest without rewriting it.
"""
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import quote
from residual_channels import ROOT,nominal_states

MASTER=ROOT/'research/HALV_TELJES_KUTATAS.md'
MANIFEST=ROOT/'research/data/master_document_manifest.json'


def link(path):
    relative=os.path.relpath(path,MASTER.parent)
    return quote(relative,safe='/')


def rebase_headings(text,shift):
    lines=[];fence=None
    for line in text.splitlines():
        hit=re.match(r'^\s{0,3}(`{3,}|~{3,})',line)
        if hit:
            token=hit.group(1)
            if fence is None:fence=token
            elif token[0]==fence[0] and len(token)>=len(fence):fence=None
        heading=re.match(r'^(#{1,6}) (.*)$',line)
        if heading and fence is None:line='#'*min(6,len(heading.group(1))+shift)+' '+heading.group(2)
        lines.append(line)
    return '\n'.join(lines)+'\n'


def main():
    overview=ROOT/'research/MASTER_OVERVIEW.md'
    journal=ROOT/'research/LOG.md';hypotheses=ROOT/'research/HYPOTHESES.md'
    reports=sorted((ROOT/'research').glob('REPORT_*.md'))
    models=sorted((ROOT/'research/models').glob('*.json'))
    section_paths=[overview,journal,hypotheses]+reports+models
    inventory={}
    for directory,role in [('research/data','eredmény/adat'),('research/sources','forrás'),
                           ('research/models','rögzített modell'),('tools','program')]:
        for p in sorted((ROOT/directory).glob('*')):
            if p.is_file() and p!=MANIFEST:inventory[p]=role
    for p in section_paths+[ROOT/'AGENTS.md',ROOT/'README.md']:inventory[p]='dokumentum' if p not in inventory else inventory[p]
    records=[]
    for p,role in sorted(inventory.items()):
        records.append({'path':str(p.relative_to(ROOT)),'role':role,'bytes':p.stat().st_size,
                        'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    append_state=ROOT/'research/data/master_append_state.json'
    if MASTER.exists() and not append_state.exists():
        raise RuntimeError('Append metadata missing; refusing to rewrite the existing master MD')
    if append_state.exists():
        from append_master_chapter import validate_append_state
        state=json.loads(append_state.read_text());data=validate_append_state(state)
        rounds=len(re.findall(r'^## 20\d\d-',journal.read_text(),re.M))
        assert rounds==state['base_journal_rounds']+len(state['chapters']),'Append the new journal round before indexing'
        base=state['base_snapshot_manifest']
        assert set(base['full_reports_embedded'])=={str(p.relative_to(ROOT)) for p in reports},'Append to the existing MD; do not create another report MD'
        embedded_models=base['full_model_specs_embedded']+[r['path'] for c in state['chapters'] for r in c['model_inputs']]
        assert set(embedded_models)=={str(p.relative_to(ROOT)) for p in models},'Unappended model specification'
        manifest={'purpose':'Append-only full research MD; old snapshot plus new end chapters',
                  'mode':'append_only','master_path':str(MASTER.relative_to(ROOT)),
                  'master_sha256':hashlib.sha256(data).hexdigest(),
                  'frozen_prefix_bytes':state['base_prefix_bytes'],'frozen_prefix_sha256':state['base_prefix_sha256'],
                  'base_snapshot_journal_rounds':state['base_journal_rounds'],'journal_round_headings':rounds,
                  'all_journal_rounds_present':True,'full_journal_embedded_as_one_current_snapshot':False,
                  'full_reports_embedded':base['full_reports_embedded'],'full_model_specs_embedded':embedded_models,
                  'appended_chapters':state['chapters'],'inputs':records,'generator':'tools/build_master_document.py',
                  'note':'Base source hashes are historical snapshots in master_append_state; inputs here describe current files.'}
        MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        print('Master MD validated without rewriting:',rounds,'rounds;',len(state['chapters']),'end appendices.')
        return
    out=['# HALV – teljes kutatási jegyzőkönyv\n',
         'A felhasználó kérésére összeállított, folyamatosan frissülő fő MD.\n',
         '**Generált fájl:** a forrásdokumentumokat frissítsd, majd futtasd az indexelőt. '
         'A teljes mentett napló és minden részletes jelentés be van ágyazva; '
         'a nagy adatok és programok hash-sel hivatkozva szerepelnek.\n',
         'Tartalom: [állapot](#state) · [alapadatok](#data) · [teljes napló](#journal) · '
         '[hipotézisek](#hypotheses) · [részletes jelentések](#reports) · '
         '[modellreceptek](#models) · [bizonyítékjegyzék](#evidence).\n',
         '<a id="state"></a>\n\n'+overview.read_text()]
    out += ['<a id="data"></a>\n\n## Névleges bemenet, egy helyen\n',
            'A forráskép: [cryptoHALV.png](sources/cryptoHALV.png). '
            'A következő sorok a mért névleges q-állapotok, nem megfejtett szöveg. '
            'A skála és mintarács modellfüggő mérési eredmény.\n',
            ]
    qtable=['| Blokk | Skála (px) | 32 egymást követő q-érték |','| --- | ---: | --- |']
    for b,row in enumerate(nominal_states().reshape(8,32)):
        qtable.append(f'| {b+1} | {128//2**b} | `'+''.join(map(str,row))+'` |')
    out.append('\n'.join(qtable))
    embedded=[]
    def add_document(path,shift=2):
        raw=path.read_text();body=rebase_headings(raw,shift)
        out.append(f'Forrás: [{path.name}]({link(path)}), SHA-256: `'+hashlib.sha256(path.read_bytes()).hexdigest()+'`.\n')
        out.append(body);embedded.append((path,body))
    out.append('<a id="journal"></a>\n\n## Teljes kronológiai napló – az első körtől\n')
    add_document(journal,1)
    out.append('<a id="hypotheses"></a>\n\n## Teljes hipotézistérkép\n');add_document(hypotheses,1)
    out.append('<a id="reports"></a>\n\n## Minden részletes jelentés\n')
    out.append('A jelentések fájlnév szerint rendezettek; az időrendi sorrendet a teljes napló tartalmazza.\n')
    for p in reports:add_document(p,2)
    out.append('<a id="models"></a>\n\n## Minden rögzített modellrecept\n')
    for p in models:
        raw=p.read_text();json.loads(raw)
        out.append(f'### {p.name}\n\nForrás: [{p.name}]({link(p)}).\n\n```json\n'+raw.rstrip()+'\n```\n')
    out.append('<a id="evidence"></a>\n\n## Teljes bizonyíték- és programjegyzék\n')
    out.append('A generált fő MD, saját manifesztje és a RUN_INDEX nem bemeneti '
               'forrás, így nincs körkörös hash-függés. A teljes index külön '
               '[RUN_INDEX.json](RUN_INDEX.json). Az összeállítás manifesztje '
               '[master_document_manifest.json](data/master_document_manifest.json).\n')
    table=['| Fájl | Szerep | Bájt | SHA-256 |','| --- | --- | ---: | --- |']
    for record in records:
        p=ROOT/record['path']
        table.append(f'| [{record["path"]}]({link(p)}) | {record["role"]} | {record["bytes"]} | `{record["sha256"]}` |')
    out.append('\n'.join(table))
    text='\n\n'.join(out)+'\n'
    for p,body in embedded:assert body in text,str(p)
    MASTER.write_text(text)
    manifest={'purpose':'Inputs and completeness of the continuously refreshed full research MD',
              'master_path':str(MASTER.relative_to(ROOT)),'master_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),
              'journal_round_headings':len(re.findall(r'^## 20\d\d-',journal.read_text(),re.M)),
              'full_journal_embedded':True,'full_hypothesis_map_embedded':True,
              'full_reports_embedded':[str(p.relative_to(ROOT)) for p in reports],
              'full_model_specs_embedded':[str(p.relative_to(ROOT)) for p in models],
              'inputs':records,'generator':'tools/build_master_document.py'}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Master MD:',len(text.splitlines()),'lines;',manifest['journal_round_headings'],'journal rounds;',len(reports),'full reports;',len(models),'model specs.')


if __name__=='__main__':main()
