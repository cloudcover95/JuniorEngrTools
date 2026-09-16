# Image modulate (end user)

```bash
python3 scripts/resize_images.py scan.png out.png --preset portrait --mode crop
python3 scripts/resize_images.py scan.png out.png --w 1080 --h 1920 --mode pad
```

Presets: portrait 750x1500, landscape 1500x750, dash 1920x1080, square 1024.
Omega consumes the PNG/OBJ side; this is the 2D sheet.
PIL extra. OSai job note: "dxf title block" / "scan jpeg".
