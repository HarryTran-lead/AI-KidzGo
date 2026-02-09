Param(
    [string]$Branch = "main",

    # Đường dẫn tới source code AI-KidzGo trên VPS
    [string]$ProjectPath = "C:\Users\Administrator\Desktop\Projects\AI-KidzGo",

    # Đường dẫn tới virtualenv dùng cho service
    [string]$VenvPath = "C:\apps\ai-kidzgo-venv",

    # Tên Windows Service đang host API FastAPI (tạo sẵn bằng NSSM/sc)
    [string]$ServiceName = "KidzgoAIService"
)

Write-Host "==== AI-KidzGo Python deploy script (Windows) ====" -ForegroundColor Cyan

function Stop-ServiceSafe {
    param([string]$Name)
    try {
        $svc = Get-Service -Name $Name -ErrorAction Stop
        if ($svc.Status -eq 'Running') {
            Write-Host "Stopping service $Name..." -ForegroundColor Yellow
            Stop-Service -Name $Name -Force -ErrorAction Stop
            $svc.WaitForStatus('Stopped','00:00:20')
        }
    }
    catch {
        Write-Host "Service $Name not found or cannot be stopped (may be first deploy)." -ForegroundColor DarkYellow
    }
}

function Start-ServiceSafe {
    param([string]$Name)
    try {
        Write-Host "Starting service $Name..." -ForegroundColor Yellow
        Start-Service -Name $Name -ErrorAction Stop
        $svc = Get-Service -Name $Name
        $svc.WaitForStatus('Running','00:00:20')
        Write-Host "Service $Name is running." -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: Could not start service $Name" -ForegroundColor Red
        throw
    }
}

Write-Host "`nStep 1/5: Go to project directory" -ForegroundColor Cyan
Set-Location $ProjectPath

Write-Host "`nStep 2/5: Pull latest code from branch '$Branch'" -ForegroundColor Cyan
git fetch origin
git checkout $Branch
git pull origin $Branch

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: git pull failed, aborting deploy." -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 3/5: Stop Windows service '$ServiceName'" -ForegroundColor Cyan
Stop-ServiceSafe -Name $ServiceName

Write-Host "`nStep 4/5: Setup virtualenv & install dependencies" -ForegroundColor Cyan

# Kiểm tra Python
Write-Host "Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found in PATH!" -ForegroundColor Red
    exit 1
}

# Tạo venv nếu chưa có
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtualenv at $VenvPath ..." -ForegroundColor Yellow
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtualenv!" -ForegroundColor Red
        exit 1
    }
}

$PipExe = Join-Path $VenvPath "Scripts\pip.exe"

if (-not (Test-Path $PipExe)) {
    Write-Host "ERROR: pip.exe not found in venv! ($PipExe)" -ForegroundColor Red
    exit 1
}

Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $PipExe install --upgrade pip

Write-Host "Installing requirements.txt..." -ForegroundColor Yellow
& $PipExe install -r (Join-Path $ProjectPath "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 5/5: Start Windows service '$ServiceName'" -ForegroundColor Cyan
Start-ServiceSafe -Name $ServiceName

Write-Host "`n✅ Deploy AI-KidzGo completed successfully." -ForegroundColor Green
Write-Host "API should now be available at configured URL/port on the VPS." -ForegroundColor Green


