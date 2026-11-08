import re,json,html
URL='https://xucadev.github.io/xucaphe-media/'
YT='https://www.youtube.com/channel/UCQFpMNDpNK0lT_W1X9ETfnw'
def si(n): return re.search(r' d="([^"]*)"',open(f'node_modules/simple-icons/icons/{n}.svg').read()).group(1)
ic={n:f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{si(n)}"/></svg>' for n in 'youtube tiktok instagram facebook threads bluesky pinterest whatsapp'.split()}
lin=lambda d:f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
svg={'candado':lin('<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/><path d="M12 15v2"/>'),
 'telefono':lin('<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/><path d="M15 3l6 6M21 3l-6 6"/>'),
 'pregunta':lin('<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 4.9.8c0 1.7-2.4 2.2-2.4 3.7"/><path d="M12 17h.01"/>')}
check=lin('<path d="M20 6 9 17l-5-5"/>')
reels=[('1000-llamada-banco','La llamada falsa del banco'),('1300-foto-ver-una-vez','La foto de "ver una vez"'),('1300-whatsapp-sin-clic','Te hackean WhatsApp sin un clic'),('1000-multa-pgr','La multa falsa por mensaje'),('1200-neveras-hackeadas','Neveras hackeadas'),('1000-likes-pagados','Te pagan por dar likes')]
R='\n      '.join(f'<a role="listitem" href="{YT}/shorts" rel="noopener"><img src="assets/img/reel-{f}.webp" alt="Portada del video: {html.escape(t)}" width="360" height="640" loading="lazy"><span>{html.escape(t)}</span></a>' for f,t in reels)
ld={"@context":"https://schema.org","@graph":[
 {"@type":"Organization","@id":URL+"#xucaphe","name":"Xucaphe","url":URL,"logo":URL+"icon-512.png","image":URL+"og.jpg","email":"Projectsmanagers@proton.me",
  "description":"Canal de ciberseguridad en español desde República Dominicana: estafas y hackeos reales explicados en un minuto.",
  "areaServed":"Latinoamérica","knowsLanguage":"es",
  "sameAs":[YT,"https://www.tiktok.com/@xucaphee","https://www.instagram.com/xucapheee/","https://www.facebook.com/1393879633819489","https://www.threads.com/@xucapheee","https://bsky.app/profile/xucaphe.bsky.social","https://www.pinterest.com/Xucaphe/"]},
 {"@type":"WebSite","@id":URL+"#web","url":URL,"name":"Xucaphe","inLanguage":"es","publisher":{"@id":URL+"#xucaphe"}},
 {"@type":"WebPage","@id":URL+"#pagina","url":URL,"name":"Xucaphe: estafas y hackeos reales explicados en un minuto","inLanguage":"es","isPartOf":{"@id":URL+"#web"},"about":{"@id":URL+"#xucaphe"},"primaryImageOfPage":URL+"og.jpg"}]}
def build(src,dst):
    s=open(src).read()
    s=s.replace('{{URL}}',URL).replace('{{YT}}',YT).replace('{{REELS}}',R).replace('{{check}}',check).replace('{{JSONLD}}',json.dumps(ld,ensure_ascii=False,indent=1))
    s=re.sub(r'\{\{icon:(\w+)\}\}',lambda m:ic[m.group(1)],s)
    s=re.sub(r'\{\{svg:(\w+)\}\}',lambda m:svg[m.group(1)],s)
    assert '{{' not in s, re.findall(r'\{\{[^}]*\}\}',s)
    open(dst,'w').write(s)
import sys
for a in sys.argv[1:]:
    src,dst=a.split(':');build(src,dst)
