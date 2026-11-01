#!/usr/bin/env python3
"""Append the latest complete journal round to the existing master MD.

Never rewrite existing master bytes. Persist offsets/hashes for every appendix.
The user explicitly requested end-only updates instead of new report MDs.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import quote
from residual_channels import ROOT

MASTER=ROOT/'research/HALV_TELJES_KUTATAS.md'
STATE=ROOT/'research/data/master_append_state.json'


def validate_append_state(state=None):
    state=state or json.loads(STATE.read_text());data=MASTER.read_bytes()
    first=state['base_prefix_bytes']
    assert hashlib.sha256(data[:first]).hexdigest()==state['base_prefix_sha256'],'Old MD prefix changed'
    offset=first
    for chapter in state['chapters']:
        assert chapter['offset']==offset
        length=chapter['bytes'];piece=data[offset:offset+length]
        assert len(piece)==length and hashlib.sha256(piece).hexdigest()==chapter['sha256']
        offset+=length
    assert len(data)==offset,'Unrecorded trailing content; do not overwrite it'
    return data


def source_record(name):
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    return {'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round',type=int,required=True)
    parser.add_argument('--model',action='append',default=[])
    parser.add_argument('--artifact',action='append',default=[])
    args=parser.parse_args();state=json.loads(STATE.read_text());old=validate_append_state(state)
    journal=ROOT/'research/LOG.md';raw=journal.read_text()
    headings=list(re.finditer(r'^## 20\d\d-.*$',raw,re.M))
    assert args.round==len(headings),'Append the latest complete journal round only'
    section=raw[headings[-1].start():].rstrip()+'\n'
    model_inputs=[source_record(name) for name in args.model]
    artifacts=[source_record(name) for name in args.artifact]
    pieces=['\n\n---\n\n'+f'<a id="round-{args.round}"></a>\n\n'+section,
            '### A fejezethez rögzített pontos modellreceptek\n']
    for record in model_inputs:
        path=ROOT/record['path'];text=path.read_text();json.loads(text)
        target=quote(os.path.relpath(path,MASTER.parent),safe='/')
        pieces.append(f'#### {path.name}\n\nForrás: [{path.name}]({target}), SHA-256: `{record["sha256"]}`.\n\n```json\n'+text.rstrip()+'\n```\n')
    pieces.append('### A fejezet adatai és reprodukciós programjai\n')
    table=['| Fájl | Bájt | SHA-256 |','| --- | ---: | --- |']
    for record in artifacts:
        target=quote(os.path.relpath(ROOT/record['path'],MASTER.parent),safe='/')
        table.append(f'| [{record["path"]}]({target}) | {record["bytes"]} | `{record["sha256"]}` |')
    pieces.append('\n'.join(table)+'\n')
    added='\n\n'.join(pieces).encode();digest=hashlib.sha256(added).hexdigest()
    existing=next((c for c in state['chapters'] if c['journal_round']==args.round),None)
    if existing:
        assert existing['sha256']==digest,'Past chapter changed; append a correction in a new round'
        print('Chapter already appended, bytes unchanged.');return
    assert args.round==state['base_journal_rounds']+len(state['chapters'])+1
    chapter={'journal_round':args.round,'offset':len(old),'bytes':len(added),'sha256':digest,
             'journal_section_sha256':hashlib.sha256(section.encode()).hexdigest(),
             'model_inputs':model_inputs,'artifact_inputs':artifacts}
    with MASTER.open('ab') as stream:stream.write(added)
    state['chapters'].append(chapter);STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    result=validate_append_state(state);assert result[:len(old)]==old
    print('Appended round',args.round,':',len(added),'new bytes; all',len(old),'existing bytes unchanged.')


if __name__=='__main__':main()
