---
name: Learning Lab
description: A quiet Apple-like reading workspace for the static English data-engineering course.
colors:
  blue: "#1456c0"
  blue-soft: "#eaf1fc"
  ink: "#202a37"
  muted: "#586779"
  line: "#dce3eb"
  paper: "#fff"
  ground: "#f5f7fa"
typography:
  display:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "clamp(32px, 3.6vw, 48px)"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-.035em"
  headline:
    fontSize: "23px"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "-.025em"
  title:
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "-.025em"
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif'
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.9
  label:
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.65
  code:
    fontFamily: "ui-monospace, SFMono-Regular, Consolas, monospace"
    fontSize: "13px"
    lineHeight: 1.7
rounded:
  inline-code: "4px"
  field: "8px"
  control: "9px"
  code: "11px"
  surface: "14px"
spacing:
  compact: "8px"
  control: "16px"
  inset: "20px"
  section: "24px"
  reading-gap: "36px"
components:
  button:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "9px 16px"
  button-primary:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "9px 16px"
  search:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "8px 10px"
  note-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "16px"
  resume:
    backgroundColor: "{colors.blue-soft}"
    rounded: "{rounded.surface}"
    padding: "24px 28px"
  answer-option:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "11px 13px"
---

# Design System: Learning Lab

## Overview

This document applies only to the learning website in `docs/learning/`. It does not define the production desktop application's appearance. The implemented HTML, CSS and JavaScript are the visual evidence; the user's confirmed direction is a clean, Apple-like reading workspace, built as a plain static site.

Cool surfaces, graphite text and restrained blue support detailed English explanations. System fonts, fine separators and a bounded reading measure keep the course practical and calm. Long chapter labels wrap; reasoning hints use native disclosure controls.

**Key Characteristics:**

- A persistent chapter position and direct route from reading to practice.
- Spacious reading content with compact supporting navigation.
- Explicit reading, self-check and local-save states.

## Colors

The frontmatter records the reused CSS custom properties from `docs/learning/style.css`; those values are normative.
The sidecar's generated tonal ramps are preview aids, not additional shipped CSS tokens.

Primary: **blue** identifies links, primary actions, progress and selected controls. **Blue soft** supplies the quiet background of resume and instructional surfaces.

Neutral: **ink** carries content; **muted** carries secondary explanations and labels; **line** separates groups; **paper** supports fields and controls; **ground** fills the reading workspace. The rail uses a slightly deeper cool surface. Code blocks use dark blue-gray; warnings and quiz feedback use their implemented amber and green semantic pairs, accompanied by explanatory text.

## Typography

The system sans stack handles Chinese and Latin text without downloaded fonts. Monospace is reserved for commands, code and inline technical syntax. Frontmatter body typography describes article prose; the surrounding interface uses a tighter line height (1.65).

The home display heading uses the fluid display role; article titles use (34px), becoming (29px) on phones. Article second-level and third-level headings use the headline and title roles. Prose becomes (14px) and code becomes (12px) at the mobile breakpoint. Navigation remains compact (13px); labels are secondary but readable. Course identifiers use tabular numbers.

## Layout

Desktop navigation is a fixed left rail (266px). Main content offsets by that width. The centered page is bounded at (1130px), with percentage side padding and a reading grid of up to (760px) content plus (160px) local contents, separated by (36px).

At widths up to (1200px), local contents disappear and reading becomes one column. At widths up to (760px), the rail becomes a (290px) drawer below a sticky (60px) header; main content loses its left offset, page padding becomes (24px 22px 45px), and syllabus groups stack. Above (1450px), page side padding is fixed at (65px). Tables and code scroll within their containers.

## Elevation & Depth

Resting surfaces use tonal changes and fine borders. The toast alone uses the implemented soft shadow, recorded in the sidecar. The mobile drawer uses a translucent scrim; its depth is functional.

Page arrival is a small upward reveal, the drawer slides horizontally, and the toast fades. Reduced-motion preferences disable animation and transitions.

## Shapes

Controls and tables use gently rounded corners; larger resume surfaces use the surface radius. Code has its own intermediate corner radius. Fine one-pixel borders distinguish fields, selections and section boundaries. The authored SVG mark is line-based; no raster imagery ships.

## Components

**Buttons.** White secondary controls and blue primary actions share compact padding, medium weight and a minimum height (44px). Hover changes fill and border. Visible keyboard focus uses an external blue outline; compact mobile-menu and code-copy buttons are explicit smaller exceptions.

**Search and notes.** Search has an adjacent visible label, white fill and a fine border. Notes use a labelled multiline field with a minimum height (170px), vertical resizing and a clear local-save hint.

**Navigation.** Chapter links pair tabular identifiers with titles. The active row gains a pale-blue fill, darker blue text and heavier weight; a small blue dot accompanies read state. On mobile, the labelled menu button reports expansion, Escape dismisses the drawer, focus is contained while open, and closing restores access to the reading pane.

**Resume and syllabus.** The resume surface pairs the saved chapter with one clear action. Syllabus groups are separated rows with explicit read labels, not decorative card grids.

**Code and tables.** Dark code surfaces pair a language label with a copy control; long lines remain horizontally scrollable. Tables have a light header, row separators and a keyboard-focusable scrolling region.

**Self-check.** Radio options use bordered white rows; selection changes both border and fill. Results include words and explanations alongside semantic color. Notes and evidence export follow the questions.

## Do's and Don'ts

- Do preserve the quiet Apple-like reading direction and system font stack.
- Do keep English instructional text, long chapter titles, code and visible learning states legible.
- Do preserve keyboard focus, labelled controls, contained overflow and reduced-motion behavior.
- Don't apply this website design system to the production desktop UI.
- Don't present reading marks or concept self-check results as proof of practical mastery.
- Don't add imagery or decorative components without a concrete reading or learning purpose.
