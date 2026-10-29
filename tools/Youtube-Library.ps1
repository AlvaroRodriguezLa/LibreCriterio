param([ValidateSet('Start','Status','Stop','Open')][string]$Action='Status',[switch]$WithoutAsr)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$pythonPath=Join-Path $projectRoot '.venv-youtube/Scripts/python.exe'
$libraryRoot=Join-Path $projectRoot 'knowledge/youtube'
$pidPath=Join-Path $libraryRoot 'batch-process.json'
function Read-Job { if(Test-Path -LiteralPath $pidPath){Get-Content -LiteralPath $pidPath -Raw|ConvertFrom-Json} }
function Get-OwnedProcess($job){
 if(-not $job){return $null}
 $process=Get-Process -Id $job.pid -ErrorAction SilentlyContinue
 if($process -and $process.StartTime.ToUniversalTime().Ticks -eq $job.startTicks -and $process.Path -eq $job.executable){return $process}
 return $null
}
if(-not(Test-Path -LiteralPath $pythonPath)){throw 'Falta el entorno local. Consulta docs/YOUTUBE_EN_MARCHA.md.'}
if($Action -eq 'Start'){
 $existing=Get-OwnedProcess (Read-Job)
 if($existing){Write-Output ('El lote ya está activo. PID '+$existing.Id);exit 0}
 New-Item -ItemType Directory -Path $libraryRoot -Force|Out-Null
 $stopPath=Join-Path $libraryRoot 'batch-stop.request';if(Test-Path -LiteralPath $stopPath){Remove-Item -LiteralPath $stopPath}
 $env:HF_HOME=Join-Path $projectRoot 'knowledge/models';$env:HF_HUB_DISABLE_XET='1';$env:PYTHONUTF8='1'
 $arguments=@('-u','tools/youtube_batch.py','--model','base')
 if(-not $WithoutAsr){$arguments+='--asr'}
 $process=Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $libraryRoot 'batch.stdout.log') -RedirectStandardError (Join-Path $libraryRoot 'batch.stderr.log')
 @{pid=$process.Id;startTicks=$process.StartTime.ToUniversalTime().Ticks;executable=$process.Path;startedAt=(Get-Date).ToUniversalTime().ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath $pidPath -Encoding utf8
 Write-Output ('Lote iniciado. PID '+$process.Id)
}elseif($Action -eq 'Stop'){
 $process=Get-OwnedProcess (Read-Job)
 if($process){(Get-Date).ToUniversalTime().ToString('o')|Set-Content -LiteralPath (Join-Path $libraryRoot 'batch-stop.request');Write-Output 'Detención solicitada. Se paran el lote y su transcripción activa; los vídeos terminados se conservan.'}else{Write-Output 'No hay un lote de este proyecto activo.'}
}elseif($Action -eq 'Open'){
 Push-Location $projectRoot
 try{& $pythonPath tools/youtube_review.py serve}finally{Pop-Location}
}else{
 $process=Get-OwnedProcess (Read-Job)
 Write-Output ('Proceso activo: '+[bool]$process)
 foreach($file in @('status.json','batch-control.json')){ $path=Join-Path $libraryRoot $file;if(Test-Path -LiteralPath $path){Get-Content -LiteralPath $path -Raw} }
}
