# Run ONCE per machine (from the repo root) in PowerShell: enables Aegis multi-machine sync hooks.
#   ./scripts/setup-sync.ps1
git config core.hooksPath .githooks
# Initial restore so transcripts already in the repo land in ~/.claude (Git Bash runs the POSIX hook).
& "$env:ProgramFiles\Git\bin\sh.exe" .githooks/post-merge 2>$null
Write-Host "Aegis sync enabled: core.hooksPath=.githooks. Commits now include the </> Code thread."
