import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const projectDir = path.resolve(scriptDir, '..')
const cli = path.join(projectDir, 'node_modules', '@dcloudio', 'vite-plugin-uni', 'bin', 'uni.js')

const result = spawnSync(process.execPath, [cli, ...process.argv.slice(2)], {
  cwd: projectDir,
  env: { ...process.env, UNI_INPUT_DIR: projectDir },
  stdio: 'inherit'
})

if (result.error) {
  console.error(result.error.message)
  process.exit(1)
}

process.exit(result.status ?? 1)
