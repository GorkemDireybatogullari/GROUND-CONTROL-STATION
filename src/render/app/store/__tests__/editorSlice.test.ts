import { describe, expect, it } from 'vitest'
import editorReducer, {
  closeEditor,
  openEditor,
  resetEditor,
  setEditorDirty,
  setEditorMode,
  setSelectedWaypoint,
} from '../editorSlice'

const initial = editorReducer(undefined, { type: '@@INIT' })

describe('editorSlice', () => {
  it('starts closed in view mode', () => {
    expect(initial).toEqual({
      isOpen: false,
      isDirty: false,
      selectedWaypointId: null,
      mode: 'view',
    })
  })

  it('openEditor opens and clears dirty flag', () => {
    const after = editorReducer({ ...initial, isDirty: true }, openEditor())
    expect(after.isOpen).toBe(true)
    expect(after.isDirty).toBe(false)
  })

  it('closeEditor resets selection, mode, and dirty', () => {
    const start = {
      ...initial,
      isOpen: true,
      isDirty: true,
      selectedWaypointId: 7,
      mode: 'edit' as const,
    }
    const after = editorReducer(start, closeEditor())
    expect(after).toEqual(initial)
  })

  it('setEditorMode updates only the mode', () => {
    const after = editorReducer(initial, setEditorMode('create'))
    expect(after.mode).toBe('create')
    expect(after.isOpen).toBe(initial.isOpen)
  })

  it('setSelectedWaypoint accepts string and number ids and null', () => {
    expect(editorReducer(initial, setSelectedWaypoint('wp_1')).selectedWaypointId).toBe('wp_1')
    expect(editorReducer(initial, setSelectedWaypoint(42)).selectedWaypointId).toBe(42)
    expect(editorReducer(initial, setSelectedWaypoint(null)).selectedWaypointId).toBeNull()
  })

  it('setEditorDirty toggles dirty state', () => {
    const after = editorReducer(initial, setEditorDirty(true))
    expect(after.isDirty).toBe(true)
  })

  it('resetEditor leaves isOpen unchanged', () => {
    const start = {
      ...initial,
      isOpen: true,
      isDirty: true,
      selectedWaypointId: 1,
      mode: 'edit' as const,
    }
    const after = editorReducer(start, resetEditor())
    expect(after.isOpen).toBe(true)
    expect(after.isDirty).toBe(false)
    expect(after.selectedWaypointId).toBeNull()
    expect(after.mode).toBe('view')
  })
})
