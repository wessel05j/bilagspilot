import { describe, expect, it } from "vitest";

import { formatMoney, statusLabel, statusTone } from "./status";

describe("status helpers", () => {
  it("maps document statuses to Norwegian labels", () => {
    expect(statusLabel("needs_review")).toBe("Må sjekkes");
    expect(statusLabel("approved")).toBe("Godkjent");
  });

  it("uses clear tones for review states", () => {
    expect(statusTone("OK")).toBe("success");
    expect(statusTone("Mangler data")).toBe("danger");
    expect(statusTone("Må sjekkes")).toBe("warning");
  });

  it("formats money for Norwegian users", () => {
    expect(formatMoney(1249, "NOK")).toContain("1 249");
  });
});

