from pathlib import Path
import sys
base=Path(__file__).parent/'assets'
base.mkdir(parents=True, exist_ok=True)
# ensure Pillow
try:
    from PIL import Image
except Exception:
    import subprocess, sys
    subprocess.check_call([sys.executable,'-m','pip','install','--user','Pillow'])
    from PIL import Image
# pick candidate images (exclude very small files)
candidates=[(f.stat().st_size,f) for f in base.iterdir() if f.is_file() and f.suffix.lower() in ('.png','.jpg','.jpeg')]
candidates=[(s,f) for s,f in candidates if s>200]
if not candidates:
    print('No suitable images found to map.')
    sys.exit(0)
candidates.sort(reverse=True)
top=[f for s,f in candidates][:4]
targets=['good.png','hungry.png','sad.png','angry.png']
for i,t in enumerate(top):
    dest=base/targets[i]
    try:
        im=Image.open(t)
        im=im.convert('RGBA')
        im.thumbnail((300,260), Image.LANCZOS)
        im.save(dest)
        print('mapped',t.name,'->',dest.name,'size',im.size)
    except Exception as e:
        print('failed',t.name,e)
print('done')
