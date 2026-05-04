import type { Waypoint } from '../../pages/cesium_map/types/waypoint.types'
import { describe, expect, it } from 'vitest'
import waypointsReducer, {
  addEditorWaypoint,
  applyEditorWaypoints,
  clearAppliedWaypoints,
  clearEditorWaypoints,
  removeEditorWaypoint,
  setAppliedWaypoints,
  setEditorWaypoints,
  setWaypointsError,
  setWaypointsLoading,
} from '../waypointsSlice'

function wp(id: string | number, lat: number, lon: number): Waypoint {
  return {
    id,
    latitude: lat,
    longitude: lon,
  }
}

const initial = waypointsReducer(undefined, { type: '@@INIT' })

describe('waypointsSlice — editor actions', () => {
  it('setEditorWaypoints replaces the editor list and clears error/saveStatus', () => {
    const after = waypointsReducer(
      { ...initial, error: 'old', saveStatus: 'error' },
      setEditorWaypoints([wp('a', 1, 2)]),
    )
    expect(after.editorWaypoints).toEqual([wp('a', 1, 2)])
    expect(after.error).toBeNull()
    expect(after.saveStatus).toBe('idle')
  })

  it('addEditorWaypoint appends without mutating the existing array', () => {
    const start = { ...initial, editorWaypoints: [wp('a', 0, 0)] }
    const after = waypointsReducer(start, addEditorWaypoint(wp('b', 1, 1)))
    expect(after.editorWaypoints).toHaveLength(2)
    expect(start.editorWaypoints).toHaveLength(1) // immutability check
  })

  it('removeEditorWaypoint filters by id', () => {
    const start = { ...initial, editorWaypoints: [wp('a', 0, 0), wp('b', 1, 1)] }
    const after = waypointsReducer(start, removeEditorWaypoint('a'))
    expect(after.editorWaypoints).toEqual([wp('b', 1, 1)])
  })

  it('removeEditorWaypoint is a no-op when id missing', () => {
    const start = { ...initial, editorWaypoints: [wp('a', 0, 0)] }
    const after = waypointsReducer(start, removeEditorWaypoint('missing'))
    expect(after.editorWaypoints).toEqual([wp('a', 0, 0)])
  })

  it('clearEditorWaypoints empties the editor list', () => {
    const start = { ...initial, editorWaypoints: [wp('a', 0, 0)] }
    const after = waypointsReducer(start, clearEditorWaypoints())
    expect(after.editorWaypoints).toEqual([])
  })
})

describe('waypointsSlice — applied actions', () => {
  it('setAppliedWaypoints replaces the applied list', () => {
    const after = waypointsReducer(initial, setAppliedWaypoints([wp('a', 1, 2)]))
    expect(after.appliedWaypoints).toEqual([wp('a', 1, 2)])
  })

  it('applyEditorWaypoints copies editor → applied without sharing reference', () => {
    const start = { ...initial, editorWaypoints: [wp('a', 0, 0)] }
    const after = waypointsReducer(start, applyEditorWaypoints())
    expect(after.appliedWaypoints).toEqual(start.editorWaypoints)
    expect(after.appliedWaypoints).not.toBe(start.editorWaypoints)
  })

  it('clearAppliedWaypoints empties applied but leaves editor untouched', () => {
    const start = {
      ...initial,
      editorWaypoints: [wp('a', 0, 0)],
      appliedWaypoints: [wp('b', 1, 1)],
    }
    const after = waypointsReducer(start, clearAppliedWaypoints())
    expect(after.appliedWaypoints).toEqual([])
    expect(after.editorWaypoints).toEqual([wp('a', 0, 0)])
  })
})

describe('waypointsSlice — utility actions', () => {
  it('setWaypointsLoading(true) sets saveStatus=loading and clears error', () => {
    const after = waypointsReducer({ ...initial, error: 'x' }, setWaypointsLoading(true))
    expect(after.isLoading).toBe(true)
    expect(after.error).toBeNull()
    expect(after.saveStatus).toBe('loading')
  })

  it('setWaypointsLoading(false) leaves error/saveStatus alone', () => {
    const start = { ...initial, isLoading: true, error: 'x', saveStatus: 'error' as const }
    const after = waypointsReducer(start, setWaypointsLoading(false))
    expect(after.isLoading).toBe(false)
    expect(after.error).toBe('x')
    expect(after.saveStatus).toBe('error')
  })

  it('setWaypointsError populates error and stops loading', () => {
    const start = { ...initial, isLoading: true }
    const after = waypointsReducer(start, setWaypointsError('boom'))
    expect(after.error).toBe('boom')
    expect(after.isLoading).toBe(false)
    expect(after.saveStatus).toBe('error')
  })
})
