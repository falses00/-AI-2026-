<# 
    Render 快速部署脚本
    
    使用方法：
    1. 打开PowerShell
    2. cd "i:\Study FastAPI"
    3. .\guides\deploy.ps1
#>

# 配置
$API_KEY = "rnd_W5XxUOsG7zgJycH8VbqBXyXb3A6Q"
$headers = @{ 
    "Authorization" = "Bearer $API_KEY"
    "Content-Type" = "application/json"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Render 快速部署工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取服务信息
Write-Host "📡 获取服务信息..." -ForegroundColor Yellow
try {
    $services = Invoke-RestMethod -Uri "https://api.render.com/v1/services?limit=1" -Headers $headers -Method Get
    $service = $services[0].service
    $serviceId = $service.id
    $serviceName = $service.name
    $serviceUrl = $service.serviceDetails.url
    
    Write-Host "✅ 服务名称: $serviceName" -ForegroundColor Green
    Write-Host "✅ 服务ID: $serviceId" -ForegroundColor Green
    Write-Host "✅ 公网URL: https://$serviceUrl" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ 获取服务信息失败: $_" -ForegroundColor Red
    exit 1
}

# 触发部署
Write-Host "🚀 触发部署..." -ForegroundColor Yellow
try {
    $deploy = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys" `
        -Headers $headers `
        -Method Post `
        -Body '{"clearCache":"do_not_clear"}'
    
    $deployId = $deploy.id
    Write-Host "✅ 部署已触发！" -ForegroundColor Green
    Write-Host "   部署ID: $deployId" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ 触发部署失败: $_" -ForegroundColor Red
    exit 1
}

# 提示
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署信息" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏱️  部署通常需要 2-5 分钟" -ForegroundColor Yellow
Write-Host "🔗 公网链接: https://$serviceUrl" -ForegroundColor Cyan
Write-Host "📊 查看进度: https://dashboard.render.com" -ForegroundColor Gray
Write-Host ""
Write-Host "完成！" -ForegroundColor Green
