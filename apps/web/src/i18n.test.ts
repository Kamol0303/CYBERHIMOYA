import { describe, expect, it } from "vitest";
import { locales, t, tCode, type MessageKey } from "./i18n/messages";

const REQUIRED_KEYS: MessageKey[] = [
  "brand",
  "cta",
  "rateLimited",
  "offlineBanner",
  "erasureTitle",
  "erasureBody",
  "erasureCta",
  "erasureConfirm",
  "erasureDone",
  "erasureFail",
  "aq039Pending",
  "emergencySimulate",
  "reason.ti_domain_hit",
  "reason.no_ti_hit",
  "action.block_and_warn",
  "action.allow",
  "action.do_not_open",
];

describe("i18n", () => {
  it("returns uz brand", () => {
    expect(t("uz", "brand")).toBe("Cyber Guardian AI");
  });

  it("covers all locales for cta", () => {
    expect(t("uz", "cta")).toBeTruthy();
    expect(t("ru", "cta")).toBeTruthy();
    expect(t("en", "cta")).toBeTruthy();
  });

  it("has locale parity for reason/action/emergency keys", () => {
    for (const locale of locales) {
      for (const key of REQUIRED_KEYS) {
        expect(t(locale, key).length).toBeGreaterThan(0);
      }
    }
  });

  it("tCode resolves action and reason codes", () => {
    expect(tCode("en", "block_and_warn")).toMatch(/block/i);
    expect(tCode("en", "reason.ti_domain_hit")).toMatch(/threat/i);
    expect(tCode("en", "UNKNOWN_CODE")).toBe("UNKNOWN_CODE");
  });
});
