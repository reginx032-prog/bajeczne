$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$photos = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'chihuahua-import.json') -Raw | ConvertFrom-Json
$font = [System.Drawing.Font]::new('Segoe UI', 12)
for ($start = 0; $start -lt $photos.Count; $start += 12) {
  $sheet = [System.Drawing.Bitmap]::new(1200, 1242)
  $g = [System.Drawing.Graphics]::FromImage($sheet)
  $g.Clear([System.Drawing.Color]::FromArgb(245,242,235))
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  for ($slot = 0; $slot -lt 12 -and ($start+$slot) -lt $photos.Count; $slot++) {
    $entry = $photos[$start+$slot]
    $photo = [System.Drawing.Image]::FromFile((Join-Path 'C:\Users\Admin\Desktop\nowy miot' $entry.source))
    $x = ($slot % 4) * 300 + 6
    $y = [Math]::Floor($slot / 4) * 414
    $dest = [System.Drawing.RectangleF]::new([single]$x, [single]$y, 288, 384)
    $src = [System.Drawing.RectangleF]::new([single]$entry.rect[0], [single]$entry.rect[1], [single]$entry.rect[2], [single]$entry.rect[3])
    $g.DrawImage($photo, $dest, $src, [System.Drawing.GraphicsUnit]::Pixel)
    $g.DrawString(('Zdjecie {0:D2}' -f $entry.id), $font, [System.Drawing.Brushes]::Black, [single]$x, [single]($y+387))
    $photo.Dispose()
  }
  $sheet.Save((Join-Path $PSScriptRoot ('chihuahua-crops-{0}.jpg' -f ([Math]::Floor($start/12)+1))), [System.Drawing.Imaging.ImageFormat]::Jpeg)
  $g.Dispose()
  $sheet.Dispose()
}
$font.Dispose()
Write-Output 'Saved 6 preview sheets with the gallery crops.'
