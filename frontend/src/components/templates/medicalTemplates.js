/**
 * Predefined templates for medical document anonymization
 * These templates are optimized for German medical discharge letters (Entlassbriefe)
 */

export const medicalTemplates = {
  "medical-standard": {
    name: "Medizinischer Standard",
    description: "Standard-Anonymisierung für medizinische Entlassbriefe mit Pseudonymisierung für Personennamen und Schwärzung für andere PIIs",
    defaultMechanism: {
      mechanism: "suppression",
      config: { suppressionChar: "X" },
    },
    mechanismsByTag: {
      PER: {
        mechanism: "pseudonymization",
        config: {},
      },
      LOC: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      ORG: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      DATE: {
        mechanism: "generalization",
        config: { generalizeType: "month" },
      },
      PHONE: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      EMAIL: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
    },
  },
  "medical-high-privacy": {
    name: "Medizinisch - Hoher Datenschutz",
    description: "Maximaler Datenschutz für medizinische Dokumente - alle PIIs werden geschwärzt",
    defaultMechanism: {
      mechanism: "suppression",
      config: { suppressionChar: "X" },
    },
    mechanismsByTag: {
      PER: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      LOC: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      ORG: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      DATE: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      PHONE: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      EMAIL: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      MISC: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      NUMBER: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
    },
  },
  "medical-research": {
    name: "Medizinisch - Forschung",
    description: "Für Forschungszwecke optimiert mit Pseudonymisierung für Personen und Generalisierung für Daten",
    defaultMechanism: {
      mechanism: "pseudonymization",
      config: {},
    },
    mechanismsByTag: {
      PER: {
        mechanism: "pseudonymization",
        config: {},
      },
      LOC: {
        mechanism: "generalization",
        config: { generalizeType: "city" },
      },
      ORG: {
        mechanism: "pseudonymization",
        config: {},
      },
      DATE: {
        mechanism: "generalization",
        config: { generalizeType: "year" },
      },
      PHONE: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
      EMAIL: {
        mechanism: "suppression",
        config: { suppressionChar: "X" },
      },
    },
  },
};

export default medicalTemplates;
