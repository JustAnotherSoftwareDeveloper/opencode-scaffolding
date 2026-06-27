import { describe, expect, test } from 'bun:test'
import { exampleMessage } from '../src/lib/example/core.ts'

describe('exampleMessage', () => {
  test('returns correct greeting for a given name', () => {
    expect(exampleMessage('World')).toBe('Hello from Node scripts, World!')
  })

  test('returns greeting for an empty string', () => {
    expect(exampleMessage('')).toBe('Hello from Node scripts, !')
  })

  test('returns greeting for another name', () => {
    expect(exampleMessage('Alice')).toBe('Hello from Node scripts, Alice!')
  })

  test('handles names with special characters', () => {
    expect(exampleMessage('John Doe')).toBe('Hello from Node scripts, John Doe!')
  })
})