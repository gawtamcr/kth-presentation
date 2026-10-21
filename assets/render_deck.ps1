param([string]$In, [string]$Out)
# Export every slide of a deck to PNG through the installed PowerPoint (read-only open, no window).
$ErrorActionPreference = 'Stop'
$app = New-Object -ComObject PowerPoint.Application
$before = $app.Presentations.Count
$pres = $app.Presentations.Open($In, -1, 0, 0)
foreach ($s in $pres.Slides) { $s.Export(($Out + '\S{0:D2}.png' -f $s.SlideIndex), 'PNG', 1600, 900) }
$pres.Close()
if ($before -eq 0) { $app.Quit() }
'done'
