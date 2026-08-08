/**
 * The navigation rail — the application menu, and the only place every part of
 * the app is named.
 *
 * Before this there was a row of six unlabelled icons, so nothing could be
 * found without hovering it. The rail collapses to icons for the compact
 * window and expands to labels for the working one, and the choice is
 * remembered.
 *
 * A pure view (CLAUDE.md rule 1). The collapse state is the one thing it owns,
 * and it is view state — where the window puts its own furniture, not
 * anything about the conversation — so `localStorage` is the right home for
 * it and the sidecar never hears about it.
 */

import { motion } from 'framer-motion'
import { useCallback, useEffect, useState } from 'react'

import { Orb } from '@/components/Orb'
import type { AssistantState } from '@/types/bridge'

export type Section = 'history' | 'voice' | 'tools' | 'settings'

const COLLAPSE_KEY = 'aria.sidebar.collapsed'

/** Read once at module load; the setter keeps it in step. */
function storedCollapsed(): boolean {
  try {
    return localStorage.getItem(COLLAPSE_KEY) === 'true'
  } catch {
    // Private mode, or storage disabled. Expanded is the better default:
    // labels are what makes this navigable at all.
    return false
  }
}

export interface UseSidebar {
  collapsed: boolean
  toggle: () => void
}

export function useSidebar(): UseSidebar {
  const [collapsed, setCollapsed] = useState(storedCollapsed)

  useEffect(() => {
    try {
      localStorage.setItem(COLLAPSE_KEY, String(collapsed))
    } catch {
      /* nothing to do — the rail still works, it just forgets */
    }
  }, [collapsed])

  const toggle = useCallback(() => setCollapsed((c) => !c), [])
  return { collapsed, toggle }
}

interface SidebarProps {
  collapsed: boolean
  onToggleCollapsed: () => void
  /** Whether labels will fit. False in the compact window, where the rail is
   *  icons-only whatever the stored preference says — measured on screen, a
   *  13rem labelled rail takes half of a 420px window and squeezes the
   *  conversation into a column. */
  canExpand: boolean
  active: Section | null
  onSelect: (section: Section) => void
  onNewChat: () => void
  canNewChat: boolean
  connected: boolean
  orbState: AssistantState
  orbLevel: number
  /** Shown as a dot on the Voice item, so hands-free state reads without
   *  opening the panel. */
  listening: boolean
}

export function Sidebar({
  collapsed: preferCollapsed,
  onToggleCollapsed,
  canExpand,
  active,
  onSelect,
  onNewChat,
  canNewChat,
  connected,
  orbState,
  orbLevel,
  listening,
}: SidebarProps): JSX.Element {
  // The window has the final say. A preference to show labels cannot conjure
  // the width to show them in.
  const collapsed = preferCollapsed || !canExpand
  return (
    <nav
      aria-label="Main"
      className={`glass-panel relative z-20 flex shrink-0 flex-col border-r border-white/5 py-2 transition-[width] duration-200 ease-out ${
        collapsed ? 'w-[3.25rem] px-1.5' : 'w-52 px-2'
      }`}
      style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
    >
      {/* Brand. The orb is the assistant-state indicator and lives here so it
          is visible whatever panel is open. */}
      <div className={`flex items-center gap-2 pb-2 ${collapsed ? 'justify-center' : 'px-1.5'}`}>
        <Orb state={orbState} connected={connected} size={20} level={orbLevel} />
        {!collapsed && (
          <span className="flex-1 truncate text-small font-semibold tracking-tight">Aria</span>
        )}
        {!collapsed && canExpand && (
          <button
            type="button"
            aria-label="Collapse sidebar"
            title="Collapse sidebar"
            onClick={onToggleCollapsed}
            className="interactive grid h-6 w-6 place-items-center rounded-md text-aria-faint hover:text-aria-text"
          >
            <IconChevron direction="left" />
          </button>
        )}
      </div>

      <Item
        icon={<IconPlus />}
        label="New chat"
        hint="New chat (Ctrl+N)"
        collapsed={collapsed}
        disabled={!connected || !canNewChat}
        onClick={onNewChat}
      />

      <div className="my-1.5 h-px bg-white/5" />

      <Item
        icon={<IconHistory />}
        label="Chats"
        hint="Chats (Ctrl+K)"
        collapsed={collapsed}
        active={active === 'history'}
        disabled={!connected}
        onClick={() => onSelect('history')}
      />
      <Item
        icon={<IconWave />}
        label="Voice"
        collapsed={collapsed}
        active={active === 'voice'}
        disabled={!connected}
        marker={listening}
        onClick={() => onSelect('voice')}
      />
      <Item
        icon={<IconTool />}
        label="Tools"
        collapsed={collapsed}
        active={active === 'tools'}
        disabled={!connected}
        onClick={() => onSelect('tools')}
      />

      <div className="mt-auto" />

      <Item
        icon={<IconGear />}
        label="Settings"
        collapsed={collapsed}
        active={active === 'settings'}
        onClick={() => onSelect('settings')}
      />

      {collapsed && canExpand && (
        <Item
          icon={<IconChevron direction="right" />}
          label="Expand sidebar"
          hint="Expand sidebar"
          collapsed
          onClick={onToggleCollapsed}
        />
      )}
    </nav>
  )
}

// ── one row ───────────────────────────────────────────────────────────

function Item({
  icon,
  label,
  hint,
  collapsed,
  active = false,
  disabled = false,
  marker = false,
  onClick,
}: {
  icon: React.ReactNode
  label: string
  hint?: string
  collapsed: boolean
  active?: boolean
  disabled?: boolean
  marker?: boolean
  onClick: () => void
}): JSX.Element {
  return (
    <button
      type="button"
      // Collapsed, the label is only in the tooltip and the accessible name,
      // so both have to carry it.
      aria-label={label}
      aria-current={active ? 'page' : undefined}
      title={hint ?? label}
      disabled={disabled}
      onClick={onClick}
      className={`interactive relative flex h-8 shrink-0 items-center gap-2.5 rounded-lg text-small disabled:cursor-not-allowed disabled:opacity-30 disabled:hover:bg-transparent ${
        collapsed ? 'justify-center px-0' : 'px-2'
      } ${active ? 'bg-white/10 text-aria-text' : 'text-aria-muted hover:text-aria-text'}`}
    >
      {/* The active marker is a rail on the edge, not a colour change: the
          palette reserves saturation for assistant state. */}
      {active && (
        <motion.span
          layoutId="sidebar-active"
          className="absolute left-0 top-1.5 h-5 w-0.5 rounded-full bg-aria-accent"
          aria-hidden
        />
      )}
      <span className="grid h-4 w-4 shrink-0 place-items-center">{icon}</span>
      {!collapsed && <span className="truncate">{label}</span>}
      {marker && (
        <span
          className={`h-1.5 w-1.5 shrink-0 rounded-full bg-aria-listening ${
            collapsed ? 'absolute right-1 top-1.5' : 'ml-auto'
          }`}
          aria-hidden
        />
      )}
    </button>
  )
}

// ── icons ─────────────────────────────────────────────────────────────
// Drawn rather than imported, matching the hairline weight of the rest of the
// chrome. Six glyphs is not worth a dependency.

const stroke = {
  width: 14,
  height: 14,
  viewBox: '0 0 14 14',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.4,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
}

function IconPlus(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <path d="M7 2.8v8.4M2.8 7h8.4" />
    </svg>
  )
}

function IconHistory(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <circle cx="7" cy="7" r="5.2" />
      <path d="M7 4.2V7l1.9 1.4" />
    </svg>
  )
}

function IconWave(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <path d="M2 7h1.2M4.6 4.4v5.2M7 2.4v9.2M9.4 4.9v4.2M11.8 6.3v1.4" />
    </svg>
  )
}

function IconTool(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <path d="M9.1 2.6a2.7 2.7 0 0 0-3.4 3.4l-3.1 3.1a1 1 0 0 0 0 1.4l.9.9a1 1 0 0 0 1.4 0l3.1-3.1a2.7 2.7 0 0 0 3.4-3.4L9.7 6.3 7.7 4.3Z" />
    </svg>
  )
}

function IconGear(): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <circle cx="7" cy="7" r="2.1" />
      <path d="M7 1.6v1.3M7 11.1v1.3M12.4 7h-1.3M2.9 7H1.6M10.8 3.2l-.9.9M4.1 9.9l-.9.9M10.8 10.8l-.9-.9M4.1 4.1l-.9-.9" />
    </svg>
  )
}

function IconChevron({ direction }: { direction: 'left' | 'right' }): JSX.Element {
  return (
    <svg {...stroke} aria-hidden>
      <path d={direction === 'left' ? 'M8.6 3.4 5 7l3.6 3.6' : 'M5.4 3.4 9 7l-3.6 3.6'} />
    </svg>
  )
}
