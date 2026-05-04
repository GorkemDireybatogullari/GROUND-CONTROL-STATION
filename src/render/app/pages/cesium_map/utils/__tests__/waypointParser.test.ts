import { describe, expect, it } from 'vitest'
import { parseWaypointTxt } from '../waypointParser'

describe('parseWaypointTxt', () => {
  it('parses a clean two-column file', () => {
    const result = parseWaypointTxt('41.0,29.0\n41.1,29.1\n')
    expect(result.errors).toEqual([])
    expect(result.waypoints).toHaveLength(2)
    expect(result.waypoints[0]).toEqual({ id: 'wp_0', latitude: 41.0, longitude: 29.0 })
    expect(result.waypoints[1].id).toBe('wp_1')
  })

  it('skips empty lines and trailing whitespace', () => {
    const result = parseWaypointTxt('\n  41,29  \n\n   \n')
    expect(result.errors).toEqual([])
    expect(result.waypoints).toEqual([{ id: 'wp_0', latitude: 41, longitude: 29 }])
  })

  it('reports errors for lines with the wrong column count', () => {
    const result = parseWaypointTxt('41,29\n41,29,extra\n')
    expect(result.waypoints).toHaveLength(1)
    expect(result.errors).toHaveLength(1)
    expect(result.errors[0]).toContain('Line 2')
    expect(result.errors[0]).toContain('Invalid format')
  })

  it('reports errors for non-numeric values', () => {
    const result = parseWaypointTxt('41,29\nnope,29\n')
    expect(result.waypoints).toHaveLength(1)
    expect(result.errors[0]).toContain('Line 2')
    expect(result.errors[0]).toContain('Invalid numbers')
  })

  it('returns empty arrays for empty input', () => {
    const result = parseWaypointTxt('')
    expect(result.waypoints).toEqual([])
    expect(result.errors).toEqual([])
  })

  it('keeps id index aligned with original line index, not surviving waypoints', () => {
    // The parser uses `forEach` index; line 0 ok, line 1 invalid (bad nums),
    // line 2 ok → ids should be wp_0 and wp_2.
    const result = parseWaypointTxt('41,29\nbad,bad\n42,30\n')
    expect(result.waypoints.map(w => w.id)).toEqual(['wp_0', 'wp_2'])
  })
})
