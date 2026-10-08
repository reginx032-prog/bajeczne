# Minimalny statyczny serwer do podglądu strony Bajeczne Urwisy (wersja PowerShell, bez Node.js)
$Root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\bajeczne-urwisy"))
$Port = 4321
$Types = @{
  ".html" = "text/html; charset=utf-8"; ".css" = "text/css; charset=utf-8"
  ".js" = "text/javascript; charset=utf-8"; ".svg" = "image/svg+xml"
  ".png" = "image/png"; ".jpg" = "image/jpeg"; ".jpeg" = "image/jpeg"
  ".webp" = "image/webp"; ".ico" = "image/x-icon"; ".json" = "application/json"
  ".xml" = "application/xml"; ".txt" = "text/plain; charset=utf-8"
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()
Write-Host "Podgląd: http://localhost:$Port"

while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  $res = $ctx.Response
  try {
    $urlPath = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath)
    if ($urlPath -eq "/") { $urlPath = "/index.html" }
    $filePath = [System.IO.Path]::GetFullPath((Join-Path $Root $urlPath.TrimStart("/")))
    if (-not $filePath.StartsWith($Root)) {
      $res.StatusCode = 403
    } elseif (Test-Path -LiteralPath $filePath -PathType Leaf) {
      $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
      $res.ContentType = if ($Types.ContainsKey($ext)) { $Types[$ext] } else { "application/octet-stream" }
      $bytes = [System.IO.File]::ReadAllBytes($filePath)
      $res.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $res.StatusCode = 404
      $res.ContentType = "text/plain; charset=utf-8"
      $msg = [System.Text.Encoding]::UTF8.GetBytes("Nie znaleziono: $urlPath")
      $res.OutputStream.Write($msg, 0, $msg.Length)
    }
  } catch {
    $res.StatusCode = 500
  } finally {
    $res.Close()
  }
}
