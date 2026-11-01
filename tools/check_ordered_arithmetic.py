#!/usr/bin/env python3
"""C29: explicit byte/word halving, carry boundaries and exact geometric branch."""
import gzip
from collections import Counter
from fractions import Fraction as F
import numpy as np
from ordered_decode_common import *

def cuts(policy,mask):
    if policy=='whole256bit_word':return [0,32]
    if policy=='each32bit_block':return list(range(0,33,4))
    marked=1 if policy=='marker1_cuts' else 0
    return [0]+[4*(b+1) for b in range(7) if mask[b]==marked]+[32]

def segment_arithmetic(a,b,policy,operation,order,mask):
    result=bytearray();trace=[];boundaries=cuts(policy,mask)
    for first,last in zip(boundaries,boundaries[1:]):
        aa=bytes(int(v) for v in a[first:last]);bb=bytes(int(v) for v in b[first:last]);n=last-first;mod=1<<(8*n)
        x=int.from_bytes(aa,order);y=int.from_bytes(bb,order);s=x+y
        if operation=='sum_low_word_with_carry':value=s%mod
        elif operation=='half_sum_floor':value=s//2
        elif operation=='half_each_floor':value=x//2+y//2
        elif operation=='subtract_low_word_with_borrow':value=(x-y)%mod
        else:raise ValueError(operation)
        out=value.to_bytes(n,order);result.extend(out)
        trace.append({'first_byte':first,'last_byte_exclusive':last,'input_a_hex':aa.hex(),'input_b_hex':bb.hex(),
                      'output_hex':out.hex(),'carry_out':s//mod,'borrow_out':int(x<y),
                      'a_mod2':x%2,'b_mod2':y%2,'sum_mod2':s%2})
    return bytes(result),trace

def ripple(a,b,order,subtract=False):
    result=np.zeros(32,int);carry=0
    indices=range(31,-1,-1) if order=='big' else range(32)
    for i in indices:
        total=int(a[i])-int(b[i])-carry if subtract else int(a[i])+int(b[i])+carry
        result[i]=total%256;carry=int(total<0) if subtract else total//256
    return bytes(int(v) for v in result),carry

def area4(q,domain):
    scales=np.ones(256,dtype=int) if domain=='normalized' else 128//2**(np.arange(256)//32)
    heights=q*scales;extended=np.r_[heights,heights[-1]]
    # q/2 heights, trapezoids at3px; quarter-area numerator is exact.
    return np.array([3*(extended[4*c]+2*sum(extended[4*c+1:4*c+4])+extended[4*c+4]) for c in range(64)],dtype=np.int64)

def round4(values,kind):
    lo=values//4;rem=values%4
    if kind=='floor':return lo
    if kind=='ceil':return lo+(rem!=0)
    return lo+((rem>2)|((rem==2)&(lo%2==1)))

def arithmetic_calibration(mask):
    a=np.zeros(32,int);b=a.copy();a[0]=1;b[-1]=1
    mean,trace=segment_arithmetic(a,b,'whole256bit_word','half_sum_floor','big',mask)
    assert int.from_bytes(mean,'big')==((1<<248)+1)//2
    assert bytes(((a+b)//2).astype(np.uint8))!=mean
    a=np.full(32,255);b=np.zeros(32,int);b[-1]=1
    result,trace=segment_arithmetic(a,b,'whole256bit_word','sum_low_word_with_carry','big',mask)
    assert result==bytes(32) and trace[0]['carry_out']==1
    assert segment_arithmetic(a,b,'whole256bit_word','half_sum_floor','big',mask)[0]==(1<<255).to_bytes(32,'big')
    result,trace=segment_arithmetic(np.zeros(32,int),b,'whole256bit_word','subtract_low_word_with_borrow','big',mask)
    assert result==bytes([255])*32 and trace[0]['borrow_out']==1
    assert (1+1)//2==1 and 1//2+1//2==0
    profiles=json.loads((ROOT/'research/data/fractional_area_profiles.json').read_text());q=nominal_states().flatten()
    for domain,label in [('normalized','normalized_nodes'),('physical','physical_nodes')]:
        old=next(p for p in profiles if p['domain']==label and p['channel']=='half_q_corrected' and p['anchor']==92 and p['extent']=='radius')
        assert [F(int(v),4) for v in area4(q,domain)]==[F(v) for v in old['values64_exact']]
    return {'word_known_answers':5,'geometry_C16_vectors_matched':2,'geometry_cells_matched':128}

def main():
    settings=spec();cases=json.loads((ROOT/'research/data/ordered_control_cases.json').read_text());mask=marker()
    calibration=arithmetic_calibration(mask);payloads={};attempts=Counter();rejected=Counter();trace_samples=[];ripple_checks=0
    path=ROOT/'research/data/ordered_arithmetic_recipes.jsonl.gz'
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as log:
        def record(data,recipe,family):
            attempts[family]+=1
            if not isinstance(data,bytes):
                values=np.asarray(data);bad=np.flatnonzero((values<0)|(values>255))
                if len(bad):
                    rejected[family]+=1;row={**recipe,'status':'byte_range_rejected','bad_indices':bad.tolist(),'minimum':int(values.min()),'maximum':int(values.max())}
                    log.write((json.dumps(row,separators=(',',':'))+'\n').encode());return
                data=bytes(int(v) for v in values)
            assert len(data)==32
            row={**recipe,'family':family,'payload32_hex':data.hex(),'status':'formed'}
            payloads.setdefault(data.hex(),row);log.write((json.dumps(row,separators=(',',':'))+'\n').encode())
        for case in cases:
            bits,r=bit_arrays(case);v=nibble_values(bits);rv=nibble_values(r);cid=case['case_id']
            for packing,terms in [('main_high',16*v+rv),('residual_high',16*rv+v)]:
                a=terms[::2];b=terms[1::2];prefix={'case_id':cid,'packing':packing}
                for name in settings['C29']['byte_operations']:
                    values={'direct_sum':a+b,'half_sum_floor':(a+b)//2,'half_each_floor':a//2+b//2,
                            'half_sum_ceil':(a+b+1)//2}[name]
                    record(values,{**prefix,'operator':name},'byte_pair')
                for policy in settings['C29']['segments']:
                    for operation in settings['C29']['segment_operations']:
                        for order in settings['C29']['byte_orders']:
                            data,trace=segment_arithmetic(a,b,policy,operation,order,mask)
                            if policy=='whole256bit_word' and operation in ['sum_low_word_with_carry','subtract_low_word_with_borrow']:
                                expected,end=ripple(a,b,order,operation.startswith('subtract'))
                                assert expected==data
                                assert end==trace[0]['borrow_out' if operation.startswith('subtract') else 'carry_out'];ripple_checks+=1
                            if cid==0:trace_samples.append({**prefix,'policy':policy,'operator':operation,'byte_order':order,'trace':trace})
                            record(data,{**prefix,'operator':operation,'policy':policy,'byte_order':order},'word_pair')
            frame=case['recipe']['frame'];base_frame='absolute' if frame=='zero_position' else frame
            transformed_q=restore(unlayout(bits,frame),r,base_frame).flatten()
            for domain in ['normalized','physical']:
                numerator=area4(transformed_q,domain)
                for rounding in settings['C29']['geometry_rounders']:
                    for order in ['round_each_then_sum','sum_then_round']:
                        values=(round4(numerator[::2],rounding)+round4(numerator[1::2],rounding) if order=='round_each_then_sum'
                                else round4(numerator[::2]+numerator[1::2],rounding))
                        record(values,{'case_id':cid,'domain':domain,'rounding':rounding,'rounding_order':order},'geometry')
    dump('ordered_arithmetic_payloads.json',list(payloads.values()))
    files=['research/models/ordered_decode_v1.json','research/data/ordered_control_check.json','research/data/ordered_control_cases.json',
           'research/data/fractional_area_profiles.json','tools/check_ordered_arithmetic.py','tools/ordered_decode_common.py','tools/residual_channels.py']
    out={'model':'C29','input_sha256':hashes(files),'calibration':calibration,'independent_ripple_comparisons':ripple_checks,
         'groups':{name:{'attempts':attempts[name],'byte_range_rejections':rejected[name]} for name in attempts},
         'attempts_including_duplicates':sum(attempts.values()),'unique_formed_payloads32':len(payloads),
         'formed_payloads_may_include_invalid_scalars':True,'recipe_log':str(path.relative_to(ROOT)),
         'recipe_log_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'trace_samples':trace_samples,
         'loss_statement':settings['C29']['loss_statement'],'limitations':settings['limitations']}
    dump('ordered_arithmetic_check.json',out)
    print('C29 groups',out['groups'],'unique32byte payloads',len(payloads),'ripple checks',ripple_checks,flush=True)

if __name__=='__main__':main()
