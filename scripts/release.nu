#!/usr/bin/nu

def main [component: string, token: string] {
  if not $component in [major minor path] {
      error make {msg: "Invalid component"}
  }
  poetry version $component
  poetry install --only-root
  git commit -am 'bump version'
  git push
  git tag (poetry version -s)
  git push --tags
  poetry publish --build -u __token__ -p token
}
