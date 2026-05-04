import { expect, test } from '@playwright/test'

test.describe('renderer smoke', () => {
  test('boots without script errors', async ({ page }) => {
    const consoleErrors: string[] = []
    page.on('pageerror', err => consoleErrors.push(`pageerror: ${err.message}`))
    page.on('console', (msg) => {
      if (msg.type() === 'error')
        consoleErrors.push(`console.error: ${msg.text()}`)
    })

    const response = await page.goto('/')
    expect(response?.ok(), 'index.html should serve').toBeTruthy()

    // The React tree mounts into <div id="root">. We just need it to be present
    // and non-empty after first paint — Cesium init happens asynchronously and
    // is allowed to lag.
    const root = page.locator('#root')
    await expect(root).toBeVisible()
    await expect(root).not.toBeEmpty({ timeout: 10_000 })

    // Tolerate Cesium ION-token / network warnings; surface any genuine
    // crash-class errors that slipped through.
    const fatal = consoleErrors.filter(
      err => !/cesium|ion|token|webgl/i.test(err) && !/favicon/i.test(err),
    )
    expect(fatal, fatal.join('\n')).toEqual([])
  })
})
