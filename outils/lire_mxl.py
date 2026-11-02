import zipfile, sys, xml.etree.ElementTree as ET
FR={'C':'Do','D':'Ré','E':'Mi','F':'Fa','G':'Sol','A':'La','B':'Si'}
def lire(f):
    z=zipfile.ZipFile(f); nom=[n for n in z.namelist() if n.endswith('.xml') and 'META' not in n][0]
    root=ET.fromstring(z.read(nom))
    titre=(root.findtext('.//movement-title') or root.findtext('.//work-title') or '')
    parts=[]
    for p in root.findall('part'):
        div=1; ev=[]; key=None; t=0
        for m in p.findall('measure'):
            for el in m:
                if el.tag=='attributes':
                    if el.find('divisions') is not None: div=int(el.findtext('divisions'))
                    if el.find('key/fifths') is not None: key=int(el.findtext('key/fifths'))
                if el.tag=='note':
                    if el.find('chord') is not None: continue
                    d=int(el.findtext('duration'))/div
                    if el.find('rest') is not None: n=None
                    else:
                        st=el.findtext('pitch/step'); al=int(float(el.findtext('pitch/alter') or 0)); o=el.findtext('pitch/octave')
                        n=FR[st]+('#' if al==1 else 'b' if al==-1 else '')+o
                    tie=any(x.get('type')=='stop' for x in el.findall('tie'))
                    ferm=el.find('notations/fermata') is not None
                    ev.append([n,d,tie,ferm,m.get('number')])
                if el.tag=='backup' or el.tag=='forward': pass
        parts.append({'key':key,'ev':ev})
    return titre, parts
if __name__=='__main__':
    t,P=lire(sys.argv[1]); print(t, [p['key'] for p in P], len(P))
    for p in P: print(' '.join(f"{e[0]}:{e[1]}{'~' if e[2] else ''}{'F' if e[3] else ''}" for e in p['ev'][:40]))
