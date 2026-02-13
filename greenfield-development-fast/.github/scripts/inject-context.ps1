# scripts/inject-context.ps1

# Prevent error messages from cluttering the output
$ErrorActionPreference = "SilentlyContinue"

# --- Configuration ---
$mdFile = "code.md"  # The file you want to append

# --- 1. Gather Project Info ---
try {
    if (Test-Path "package.json") {
        $package = Get-Content "package.json" -Raw | ConvertFrom-Json
        $projectInfo = "$($package.name) v$($package.version)"
    } else {
        $projectInfo = "Unknown Project"
    }
} catch {
    $projectInfo = "Error reading package.json"
}

# --- 2. Gather Environment Info ---
$branch = git branch --show-current
if (-not $branch) { $branch = "unknown" }

$nodeVer = node -v
if (-not $nodeVer) { $nodeVer = "not installed" }

# --- 3. Read Markdown File ---
if (Test-Path $mdFile) {
    # -Raw reads the entire file as a single string, preserving newlines
    $mdContent = Get-Content $mdFile -Raw
} else {
    $mdContent = "(No context file found at $mdFile)"
}

# --- 4. Combine Context ---
# `n is the PowerShell escape character for a new line
$header = "Project: $projectInfo | Branch: $branch | Node: $nodeVer"
$finalContext = "$header`n`n--- Context File ---`n$mdContent"

# --- 5. Output JSON ---
$payload = @{
    hookSpecificOutput = @{
        hookEventName = "SessionStart"
        additionalContext = $finalContext
    }
}

# Convert hashtable to JSON and print to stdout
$payload | ConvertTo-Json -Depth 5