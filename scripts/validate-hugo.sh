#!/bin/bash
set -e

echo "🔍 Running Hugo-specific validations..."

# colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # no color

ERRORS=0

# function to print error messages
error() {
    echo -e "${RED}❌ $1${NC}"
    ERRORS=$((ERRORS + 1))
}

# function to print warning messages
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# function to print success messages
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo "📋 Validating Hugo build..."
if hugo --printI18nWarnings --printPathWarnings --printUnusedTemplates --gc --minify --quiet > /tmp/hugo-build.log 2>&1; then
    success "Hugo build completed successfully"
else
    error "Hugo build failed"
    cat /tmp/hugo-build.log
fi

echo "📋 Checking front matter consistency..."
find content/docs -name "*.md" | while IFS= read -r file; do
    # skip _index.md files for some checks
    if [[ "$file" == *"_index.md"* ]]; then
        continue
    fi

    # check for required title field
    if ! grep -q "^title\s*=" "$file"; then
        error "Missing 'title' field in $file"
    fi

    # check for weight field (required for proper ordering)
    if ! grep -q "^weight\s*=" "$file"; then
        warning "Missing 'weight' field in $file - may affect menu ordering"
    fi

    # check for description field (good for SEO)
    if ! grep -q "^description\s*=" "$file"; then
        warning "Missing 'description' field in $file - may affect SEO"
    fi
done

echo "📋 Validating content structure..."
# check for orphaned pages (pages without proper _index.md in parent directories)
find content/docs -name "*.md" ! -name "_index.md" | while IFS= read -r file; do
    dir=$(dirname "$file")
    if [ "$dir" != "content/docs" ] && [ ! -f "$dir/_index.md" ]; then
        warning "Missing _index.md in directory: $dir"
    fi
done

echo "📋 Checking for broken shortcodes..."
# look for common shortcode issues
if grep -r "{{<.*>}}" content/ --include="*.md" | grep -v "{{< \|{{</" > /tmp/shortcode-check.log; then
    if [ -s /tmp/shortcode-check.log ]; then
        warning "Potential shortcode syntax issues found:"
        cat /tmp/shortcode-check.log
    fi
fi

echo "📋 Validating menu structure..."
# check for duplicate menu weights
WEIGHTS=$(grep -r "^weight\s*=" content/docs --include="*.md" | sed 's/.*weight\s*=\s*//' | sort)
DUPLICATES=$(echo "$WEIGHTS" | uniq -d)
if [ -n "$DUPLICATES" ]; then
    warning "Duplicate menu weights found: $DUPLICATES"
fi

echo "📋 Checking for required Hugo version..."
if command -v hugo >/dev/null 2>&1; then
    HUGO_VERSION=$(hugo version | grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+')
    success "Hugo version: $HUGO_VERSION"
else
    error "Hugo is not installed or not in PATH"
fi

# cleanup
rm -f /tmp/hugo-build.log /tmp/shortcode-check.log

if [ $ERRORS -eq 0 ]; then
    success "All Hugo validations passed!"
    exit 0
else
    error "$ERRORS validation errors found"
    exit 1
fi