# Calendar Component Modifications - Summary

## Overview
Modified the DOM serializer to handle special calendar component rendering with two key improvements:

1. **Navigation Icon Descriptions**: Added `data-role` attributes to calendar navigation icons
2. **View Visibility Management**: Implemented visibility logic based on CSS `top` values

---

## Issue #1: Calendar Navigation Icon Descriptions

### Problem
Calendar navigation icons (prev-year, prev-month, next-month, next-year) had no descriptive attributes, making them hard to identify for LLMs.

### Solution
Modified `_build_attributes_string()` method to detect calendar navigation icons by their `mxs` attribute and automatically add descriptive `data-role` attributes.

### Implementation Details

**File**: `browser_use/dom/serializer/serializer.py` (lines 1146-1166)

```python
# Special handling for calendar navigation icons
if node.attributes and 'mxs' in node.attributes:
    mxs_value = node.attributes.get('mxs', '')
    calendar_nav_roles = {
        'asiYysjsD:_': 'prev-year',
        'asiYysjsD:a': 'prev-month',
        'asiYysjsD:b': 'next-month',
        'asiYysjsD:c': 'next-year',
    }
    if mxs_value in calendar_nav_roles:
        element_classes = node.attributes.get('class', '')
        if 'asiYysjsbv' in element_classes or 'asiYysjsbw' in element_classes:
            attributes_to_include['data-role'] = calendar_nav_roles[mxs_value]
```

### Mapping
| mxs Attribute | data-role Attribute | Description |
|---------------|---------------------|-------------|
| `asiYysjsD:_` | `prev-year` | Previous year button |
| `asiYysjsD:a` | `prev-month` | Previous month button |
| `asiYysjsD:b` | `next-month` | Next month button |
| `asiYysjsD:c` | `next-year` | Next year button |

### Before/After Example
**Before:**
```html
<span class="asiYysjsbv" mxs="asiYysjsD:a"></span>
```

**After:**
```html
<span class="asiYysjsbv" mxs="asiYysjsD:a" data-role="prev-month"></span>
```

---

## Issue #2: Calendar View Visibility Based on Top Values

### Problem
Calendar components with class `asiYysjsbu unselectable` contain three child views (day, month, year) with class `asiYysjsbE`. Only one view should be visible at a time, determined by which has the largest CSS `top` value.

### Solution
Added a new processing step `_handle_calendar_visibility()` that:
1. Finds calendar containers by `mxa='asiYysjsD:_'` and `class='asiYysjsbu unselectable'`
2. Identifies all child views with `class='asiYysjsbE'`
3. Extracts `top` values from each view's `style` attribute
4. Sets `should_display=False` for all views except the one with the largest `top` value

### Implementation Details

**File**: `browser_use/dom/serializer/serializer.py`

**New Methods (lines 585-653):**

1. `_handle_calendar_visibility()` - Main logic for calendar view management
```python
def _handle_calendar_visibility(self, node: SimplifiedNode | None) -> None:
    """Handle special calendar visibility logic.

    For calendar components with class 'asiYysjsbu unselectable' and mxa='asiYysjsD:_',
    only the child div with class 'asiYysjsbE' that has the largest 'top' value should be visible.
    """
    if not node:
        return

    # Check if this is a calendar container
    if (node.original_node.node_type == NodeType.ELEMENT_NODE and
        node.original_node.attributes):
        attrs = node.original_node.attributes
        classes = attrs.get('class', '')
        mxa_value = attrs.get('mxa', '')

        if ('asiYysjsbu' in classes and 'unselectable' in classes and
            mxa_value == 'asiYysjsD:_'):
            # Find all calendar views
            calendar_views = []
            for child in node.children:
                if (child.original_node.node_type == NodeType.ELEMENT_NODE and
                    child.original_node.attributes):
                    child_classes = child.original_node.attributes.get('class', '')
                    if 'asiYysjsbE' in child_classes:
                        style = child.original_node.attributes.get('style', '')
                        top_value = self._extract_top_value(style)
                        calendar_views.append((child, top_value))

            # Hide all except the one with largest top value
            if len(calendar_views) > 1:
                calendar_views.sort(key=lambda x: x[1], reverse=True)
                for i, (view, top_val) in enumerate(calendar_views):
                    if i > 0:
                        view.should_display = False

    # Recursively process children
    for child in node.children:
        self._handle_calendar_visibility(child)
```

2. `_extract_top_value()` - Helper to parse CSS top values
```python
def _extract_top_value(self, style_str: str) -> float:
    """Extract numeric top value from CSS style string."""
    import re
    if not style_str:
        return 0.0
    match = re.search(r'top:\s*([+-]?\d+(?:\.\d+)?)', style_str, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0
```

**Pipeline Integration (lines 130-135):**
```python
# Step 3.5: Handle calendar visibility based on top values
start_calendar = time.time()
if optimized_tree:
    self._handle_calendar_visibility(optimized_tree)
end_calendar = time.time()
self.timing_info['handle_calendar_visibility'] = end_calendar - start_calendar
```

### Logic Flow

```
1. Find calendar container:
   <div mxa="asiYysjsD:_" class="asiYysjsbu unselectable">

2. Find child views:
   <div class="asiYysjsbE" style="top: 100px">  <!-- Day view -->
   <div class="asiYysjsbE asiYysjsbF" style="top: 50px">  <!-- Month view -->
   <div class="asiYysjsbE asiYysjsbG" style="top: 0px">  <!-- Year view -->

3. Sort by top value:
   [(day_view, 100), (month_view, 50), (year_view, 0)]

4. Hide all except first:
   day_view.should_display = True   (largest top: 100px)
   month_view.should_display = False
   year_view.should_display = False
```

---

## Configuration Changes

### File: `browser_use/dom/views.py` (lines 53-55)

Added new attributes to `DEFAULT_INCLUDE_ATTRIBUTES`:

```python
'data-role',  # Role description for special UI elements (e.g., calendar navigation)
'mxs',  # Magix framework selector attribute (used in calendar components)
'mxa',  # Magix framework attribute (used to identify component types)
```

These attributes are now included in serialized output, allowing the calendar logic to work properly.

---

## Processing Pipeline

The calendar visibility handling is integrated as Step 3.5 in the DOM processing pipeline:

```
1. Create simplified tree
2. Apply paint order filtering
3. Optimize tree (remove unnecessary parents)
3.5. ⭐ Handle calendar visibility ⭐  <-- NEW STEP
4. Apply bounding box filtering
5. Assign interactive indices
```

---

## Testing

To test the modifications:

```bash
cd /Users/liuyichen/Documents/repo/browser-use
python3 test_calendar_modifications.py
```

Or test with the actual HTML file:
```python
from browser_use.dom.serializer.serializer import DOMTreeSerializer
# Load and serialize the calendar HTML
# Verify navigation icons have data-role attributes
# Verify only one calendar view is visible
```

---

## Files Modified

1. **browser_use/dom/serializer/serializer.py**
   - Added calendar navigation icon handling (lines 1146-1166)
   - Added `_handle_calendar_visibility()` method (lines 585-653)
   - Integrated calendar visibility into pipeline (lines 130-135)

2. **browser_use/dom/views.py**
   - Added `mxs` and `mxa` to DEFAULT_INCLUDE_ATTRIBUTES (lines 54-55)

3. **.venv/lib/python3.12/site-packages/cdp_use/client.py** (earlier modification)
   - Enhanced unicode handling for HTML retrieval (lines 315-318, 399)

---

## Expected Behavior

### Calendar Navigation Icons
All calendar navigation icons will now have descriptive `data-role` attributes:
- ⏮️ Previous Year: `data-role="prev-year"`
- ⬅️ Previous Month: `data-role="prev-month"`
- ➡️ Next Month: `data-role="next-month"`
- ⏭️ Next Year: `data-role="next-year"`

### Calendar Views
Only the active calendar view (day/month/year) will be serialized:
- If day view has highest `top` value → only day view shown
- If month view has highest `top` value → only month view shown
- If year view has highest `top` value → only year view shown

This prevents cluttering the serialized DOM with multiple inactive calendar views.
