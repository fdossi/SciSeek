$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

function Invoke-PyInstaller([switch]$Clean) {
	$args = @("-m", "PyInstaller", "--noconfirm")
	if ($Clean) { $args += "--clean" }
	$args += "sciseek.spec"

	# 1) Tenta o python ativo
	if ((Get-Command python -ErrorAction SilentlyContinue)) {
		& python -c "import PyInstaller" | Out-Null
		if ($LASTEXITCODE -eq 0) {
			& python @args
			if ($LASTEXITCODE -ne 0) {
				throw "Falha ao executar PyInstaller com o python ativo."
			}
			return
		}
		Write-Warning "PyInstaller nao encontrado no python ativo; tentando via conda..."
	}

	# 2) Fallback: conda run (env atual ou 'edx')
	if (Get-Command conda -ErrorAction SilentlyContinue) {
		$envName = $env:CONDA_DEFAULT_ENV
		if (-not $envName -or $envName -eq "base") { $envName = $env:SCISEEK_CONDA_ENV }
		if (-not $envName) { $envName = "edx" }
		& conda run -n $envName python @args
		if ($LASTEXITCODE -ne 0) {
			throw "Falha ao executar PyInstaller via conda no ambiente '$envName'."
		}
		return
	}

	throw "Nao foi possivel localizar um ambiente Python com PyInstaller."
}

try {
	Invoke-PyInstaller -Clean
}
catch {
	Write-Warning "Build com --clean falhou (possivel lock de arquivos). Tentando novamente sem --clean."
	Invoke-PyInstaller
}
