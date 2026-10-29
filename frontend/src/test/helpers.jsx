import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import axe from "axe-core";

import { AuthProvider } from "../context/AuthContext";

export function renderWithProviders(ui, { route = "/" } = {}) {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </AuthProvider>,
  );
}

/**
 * axe-core is used directly rather than through a matcher adapter, so there is
 * no runner-specific plugin to keep in step with vitest versions.
 *
 * Only serious and critical violations fail. Moderate ones are reported by
 * axe but are frequently style-level and would make the suite noisy.
 */
export async function expectNoSeriousA11yViolations(container) {
  const results = await axe.run(container, {
    rules: {
      // The test renders a fragment, not a whole document, so landmark rules
      // report false positives.
      region: { enabled: false },

      // colour-contrast needs a real rendering engine: axe reads pixels back
      // through canvas, which jsdom does not implement. It cannot produce a
      // meaningful result here, only a "Not implemented" warning on stderr.
      // Contrast has to be checked in a real browser (devtools or Lighthouse)
      // and that check recorded separately.
      "color-contrast": { enabled: false },
    },
  });

  const serious = results.violations.filter(
    (violation) => violation.impact === "serious" || violation.impact === "critical",
  );

  if (serious.length > 0) {
    const detail = serious
      .map((violation) => `  - [${violation.impact}] ${violation.id}: ${violation.help}`)
      .join("\n");
    throw new Error(`Accessibility violations found:\n${detail}`);
  }
}
