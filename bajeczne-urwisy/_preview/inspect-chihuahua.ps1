$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$sourceDir = 'C:\Users\Admin\Desktop\nowy miot'
$previewDir = $PSScriptRoot
$names = @()
$names += 1..8 | ForEach-Object { "v$_.jpeg" }
$names += @('16.15.15', '16.15.30', '16.15.47', '16.16.02', '16.16.15', '16.16.27') | ForEach-Object { "WhatsApp Image 2026-08-23 at $_.jpeg" }
$names += 1..9 | ForEach-Object { "x$_.jpeg" }
$names += @('z.jpeg')
$names += 2..8 | ForEach-Object { "z$_.jpeg" }
$names += 1..9 | ForEach-Object { "c$_.jpeg" }
$names += Get-ChildItem -LiteralPath $sourceDir -File | Where-Object Name -Like 'WhatsApp Image 2026-08-10*' | Sort-Object Name | Select-Object -ExpandProperty Name
$names += @('18.01.11', '18.02.11', '18.02.50', '18.03.38') | ForEach-Object { "WhatsApp Image 2026-08-23 at $_.jpeg" }
$manifest = @()
$font = [System.Drawing.Font]::new('Segoe UI', 11)
$small = [System.Drawing.Font]::new('Segoe UI', 8)
for ($start = 0; $start -lt $names.Count; $start += 12) {
  $sheet = [System.Drawing.Bitmap]::new(1200, 1320)
  $g = [System.Drawing.Graphics]::FromImage($sheet)
  $g.Clear([System.Drawing.Color]::FromArgb(245,242,235))
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  for ($slot = 0; $slot -lt 12 -and ($start + $slot) -lt $names.Count; $slot++) {
    $idx = $start + $slot
    $name = $names[$idx]
    $photo = [System.Drawing.Image]::FromFile((Join-Path $sourceDir $name))
    $width = $photo.Width
    $height = $photo.Height
    $x = ($slot % 4) * 300
    $y = [Math]::Floor($slot / 4) * 440
    $scale = [Math]::Min(290.0 / $width, 392.0 / $height)
    $dest = [System.Drawing.RectangleF]::new([single]($x + (300 - $width * $scale) / 2), [single]$y, [single]($width * $scale), [single]($height * $scale))
    $g.DrawImage($photo, $dest)
    $label = $name.Replace('WhatsApp Image ', '').Replace(' at ', ' ').Replace('.jpeg', '')
    $g.DrawString(('{0:D2} | {1}' -f ($idx+1), $label), $font, [System.Drawing.Brushes]::Black, [single]($x+5), [single]($y+397))
    $orientation = if ($photo.PropertyIdList -contains 274) { [BitConverter]::ToUInt16($photo.GetPropertyItem(274).Value, 0) } else { 1 }
    $g.DrawString("$width x $height | EXIF $orientation", $small, [System.Drawing.Brushes]::DimGray, [single]($x+5), [single]($y+419))
    $manifest += [pscustomobject]@{ id=$idx+1; source=$name; file=('chihuahua-2026-{0:D2}.jpg' -f ($idx+1)); width=$width; height=$height; crop=@(50,50,100) }
    $photo.Dispose()
  }
  $sheet.Save((Join-Path $previewDir ('chihuahua-originals-{0}.jpg' -f ([Math]::Floor($start/12)+1))), [System.Drawing.Imaging.ImageFormat]::Jpeg)
  $g.Dispose()
  $sheet.Dispose()
}
$font.Dispose()
$small.Dispose()
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $previewDir 'chihuahua-import.json') -Encoding UTF8
Write-Output "Prepared $($manifest.Count) photos in 6 contact sheets."
