/**
 * The splitter decides what gets re-parsed per token, so a wrong split is not
 * a performance bug — it changes what the markdown means.
 */

import { describe, expect, it } from 'vitest'

import { closeOpenFence, splitBlocks } from '@/components/Markdown.blocks'

const FENCE = '```'

describe('splitting', () => {
  it('separates paragraphs', () => {
    expect(splitBlocks('one\n\ntwo')).toEqual(['one', 'two'])
  })

  it('keeps a blank line inside fenced code', () => {
    // It is ordinary code. Splitting here would produce two code blocks with
    // the second one un-fenced, i.e. a paragraph of source.
    const text = `${FENCE}python\na = 1\n\nb = 2\n${FENCE}`

    expect(splitBlocks(text)).toEqual([text])
  })

  it('keeps a loose list together', () => {
    // `- a` / blank / `- b` is one list with spaced items. Split naively it
    // becomes two lists — and an ordered one would restart its numbering at 1,
    // which is a visible, wrong answer rather than a slow one.
    const blocks = splitBlocks('- a\n\n- b\n\n- c')

    expect(blocks).toHaveLength(1)
    expect(blocks[0]).toContain('- a')
    expect(blocks[0]).toContain('- c')
  })

  it('keeps an ordered list together', () => {
    expect(splitBlocks('1. first\n\n2. second')).toHaveLength(1)
  })

  it('keeps a wrapped list item with its list', () => {
    expect(splitBlocks('- a line\n\n  continued here')).toHaveLength(1)
  })

  it('ends a list when ordinary prose follows', () => {
    expect(splitBlocks('- a\n- b\n\nAnd then prose.')).toEqual(['- a\n- b', 'And then prose.'])
  })

  it('keeps a blockquote spanning paragraphs together', () => {
    expect(splitBlocks('> one\n\n> two')).toHaveLength(1)
  })

  it('drops blank runs rather than emitting empty blocks', () => {
    expect(splitBlocks('one\n\n\n\ntwo')).toEqual(['one', 'two'])
    expect(splitBlocks('\n\n')).toEqual([])
    expect(splitBlocks('')).toEqual([])
  })

  it('leaves everything after an unclosed fence in one block', () => {
    // Mid-stream this is the normal state, not an error: the rest of the reply
    // has not arrived yet and all of it so far is code.
    const blocks = splitBlocks(`text\n\n${FENCE}python\na = 1\n\nb = 2`)

    expect(blocks).toHaveLength(2)
    expect(blocks[1]).toContain('b = 2')
  })

  it('reconstructs the source when the blocks are rejoined', () => {
    // Nothing may be silently dropped. Blocks are rendered independently, so a
    // lost line would simply never appear on screen.
    const text = 'Intro line.\n\n- a\n- b\n\nOutro line.'
    expect(splitBlocks(text).join('\n\n')).toBe(text)
  })
})

describe('a half-written fence', () => {
  it('is closed so it renders as code from the first line', () => {
    expect(closeOpenFence(`${FENCE}python\nprint(`)).toBe(`${FENCE}python\nprint(\n${FENCE}`)
  })

  it('leaves a finished block alone', () => {
    const done = `${FENCE}python\nprint(1)\n${FENCE}`
    expect(closeOpenFence(done)).toBe(done)
  })

  it('closes with the marker that was opened', () => {
    expect(closeOpenFence('~~~js\nlet a')).toBe('~~~js\nlet a\n~~~')
  })

  it('leaves prose untouched', () => {
    expect(closeOpenFence('just a sentence')).toBe('just a sentence')
  })

  it('does not treat a lone opener as already closed', () => {
    expect(closeOpenFence(`${FENCE}python`)).toBe(`${FENCE}python\n${FENCE}`)
  })
})
