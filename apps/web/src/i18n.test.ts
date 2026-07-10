import { describe, expect, it } from "vitest";
import { t } from "./i18n/messages";

describe("i18n", () => {
  it("returns uz brand", () => {
    expect(t("uz", "brand")).toBe("Cyber Guardian AI");
  });

  it("covers all locales for cta", () => {
    expect(t("uz", "cta")).toBeTruthy();
    expect(t("ru", "cta")).toBeTruthy();
    expect(t("en", "cta")).toBeTruthy();
  });
});
