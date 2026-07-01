#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

run_pyinstaller() {
	local clean_flag="$1"
	local args=( -m PyInstaller --noconfirm )
	if [[ "$clean_flag" == "clean" ]]; then
		args+=( --clean )
	fi
	args+=( sciseek.spec )

	if python -c "import PyInstaller" >/dev/null 2>&1; then
		python "${args[@]}"
		return
	fi

	if command -v conda >/dev/null 2>&1; then
		local env_name="${CONDA_DEFAULT_ENV:-}"
		if [[ -z "$env_name" || "$env_name" == "base" ]]; then
			env_name="${SCISEEK_CONDA_ENV:-edx}"
		fi
		conda run -n "$env_name" python "${args[@]}"
		return
	fi

	echo "[ERROR] PyInstaller nao encontrado no python ativo e conda indisponivel." >&2
	return 1
}

if ! run_pyinstaller clean; then
	echo "[WARN] Build com --clean falhou; tentando sem --clean..." >&2
	run_pyinstaller noclean
fi
