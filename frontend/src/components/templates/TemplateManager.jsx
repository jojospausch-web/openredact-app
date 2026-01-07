import React, { useState, useEffect, useContext } from "react";
import {
  Button,
  Dialog,
  Classes,
  Card,
  H5,
  HTMLSelect,
  InputGroup,
  TextArea,
  Intent,
  Icon,
  Menu,
  MenuItem,
  MenuDivider,
  Popover,
  Position,
} from "@blueprintjs/core";
import PropTypes from "prop-types";
import "./TemplateManager.sass";
import PolyglotContext from "../../js/polyglotContext";
import AppToaster from "../../js/toaster";
import {
  getTemplates,
  saveTemplate,
  deleteTemplate,
  importTemplates,
  exportTemplates,
} from "../../api/routes";
import medicalTemplates from "./medicalTemplates";

const TemplateManager = ({ isOpen, onClose, currentConfig, onApplyTemplate }) => {
  const t = useContext(PolyglotContext);
  const [templates, setTemplates] = useState({});
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadTemplates();
    }
  }, [isOpen]);

  const loadTemplates = () => {
    getTemplates()
      .then((response) => {
        setTemplates(response.data.templates || {});
      })
      .catch(() => {
        AppToaster.show({
          message: t("templates.load_failed_toast") || "Failed to load templates",
          intent: "danger",
        });
      });
  };

  const handleSaveAsTemplate = () => {
    const templateId = `template-${Date.now()}`;
    const templateData = {
      name: "New Template",
      description: "",
      defaultMechanism: currentConfig.defaultMechanism,
      mechanismsByTag: currentConfig.mechanismsByTag,
    };
    setEditingTemplate({ id: templateId, data: templateData });
    setIsEditing(true);
  };

  const handleEditTemplate = (templateId) => {
    setEditingTemplate({ id: templateId, data: templates[templateId] });
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    if (!editingTemplate.data.name.trim()) {
      AppToaster.show({
        message: t("templates.name_required") || "Template name is required",
        intent: "warning",
      });
      return;
    }

    saveTemplate(editingTemplate.id, editingTemplate.data)
      .then(() => {
        loadTemplates();
        setIsEditing(false);
        setEditingTemplate(null);
        AppToaster.show({
          message: t("templates.save_success_toast") || "Template saved successfully",
          intent: "success",
        });
      })
      .catch(() => {
        AppToaster.show({
          message: t("templates.save_failed_toast") || "Failed to save template",
          intent: "danger",
        });
      });
  };

  const handleDeleteTemplate = (templateId) => {
    if (!window.confirm(t("templates.delete_confirm") || "Delete this template?")) {
      return;
    }

    deleteTemplate(templateId)
      .then(() => {
        loadTemplates();
        if (selectedTemplateId === templateId) {
          setSelectedTemplateId("");
        }
        AppToaster.show({
          message: t("templates.delete_success_toast") || "Template deleted successfully",
          intent: "success",
        });
      })
      .catch(() => {
        AppToaster.show({
          message: t("templates.delete_failed_toast") || "Failed to delete template",
          intent: "danger",
        });
      });
  };

  const handleApplyTemplate = () => {
    if (!selectedTemplateId || !templates[selectedTemplateId]) {
      AppToaster.show({
        message: t("templates.select_template") || "Please select a template",
        intent: "warning",
      });
      return;
    }

    const template = templates[selectedTemplateId];
    onApplyTemplate({
      defaultMechanism: template.defaultMechanism,
      mechanismsByTag: template.mechanismsByTag,
    });

    AppToaster.show({
      message: t("templates.apply_success_toast") || "Template applied successfully",
      intent: "success",
    });
    onClose();
  };

  const handleExport = () => {
    exportTemplates()
      .then((response) => {
        const dataStr = JSON.stringify(response.data.templates, null, 2);
        const dataBlob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `openredact-templates-${Date.now()}.json`;
        link.click();
        URL.revokeObjectURL(url);
        AppToaster.show({
          message: t("templates.export_success_toast") || "Templates exported successfully",
          intent: "success",
        });
      })
      .catch(() => {
        AppToaster.show({
          message: t("templates.export_failed_toast") || "Failed to export templates",
          intent: "danger",
        });
      });
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target.result);
        importTemplates(imported)
          .then(() => {
            loadTemplates();
            AppToaster.show({
              message: t("templates.import_success_toast") || "Templates imported successfully",
              intent: "success",
            });
          })
          .catch(() => {
            AppToaster.show({
              message: t("templates.import_failed_toast") || "Failed to import templates",
              intent: "danger",
            });
          });
      } catch (error) {
        AppToaster.show({
          message: t("templates.import_parse_error") || "Invalid template file format",
          intent: "danger",
        });
      }
    };
    reader.readAsText(file);
    event.target.value = null;
  };

  const handleLoadPredefined = () => {
    importTemplates(medicalTemplates)
      .then(() => {
        loadTemplates();
        AppToaster.show({
          message: t("templates.predefined_loaded") || "Predefined medical templates loaded successfully",
          intent: "success",
        });
      })
      .catch(() => {
        AppToaster.show({
          message: t("templates.predefined_failed") || "Failed to load predefined templates",
          intent: "danger",
        });
      });
  };

  const templateOptions = [
    { value: "", label: t("templates.select_placeholder") || "Select a template..." },
    ...Object.entries(templates).map(([id, template]) => ({
      value: id,
      label: template.name,
    })),
  ];

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={t("templates.title") || "Template Manager"}
      className="template-dialog"
    >
      <div className={Classes.DIALOG_BODY}>
        {!isEditing && (
          <>
            <p className="template-description">
              {t("templates.description") ||
                "Save and reuse anonymization configurations optimized for medical discharge letters. Templates define different anonymization mechanisms for each entity category."}
            </p>

            <Card className="template-selector-card">
              <H5>{t("templates.apply_template") || "Apply Template"}</H5>
              <HTMLSelect
                options={templateOptions}
                value={selectedTemplateId}
                onChange={(e) => setSelectedTemplateId(e.target.value)}
                fill
              />
              {selectedTemplateId && templates[selectedTemplateId] && (
                <div className="template-preview">
                  <p className="template-preview-description">
                    {templates[selectedTemplateId].description || t("templates.no_description") || "No description"}
                  </p>
                  <div className="template-actions">
                    <Button
                      icon="edit"
                      small
                      onClick={() => handleEditTemplate(selectedTemplateId)}
                    >
                      {t("templates.edit") || "Edit"}
                    </Button>
                    <Button
                      icon="trash"
                      small
                      intent="danger"
                      onClick={() => handleDeleteTemplate(selectedTemplateId)}
                    >
                      {t("templates.delete") || "Delete"}
                    </Button>
                  </div>
                </div>
              )}
            </Card>

            <div className="template-manager-actions">
              <Button icon="floppy-disk" onClick={handleSaveAsTemplate}>
                {t("templates.save_current") || "Save Current Config as Template"}
              </Button>
              <Button icon="download" onClick={handleLoadPredefined}>
                {t("templates.load_predefined") || "Load Medical Templates"}
              </Button>
              <Popover
                content={
                  <Menu>
                    <MenuItem
                      icon="export"
                      text={t("templates.export") || "Export All Templates"}
                      onClick={handleExport}
                    />
                    <MenuItem
                      icon="import"
                      text={t("templates.import") || "Import Templates"}
                      onClick={() => document.getElementById("template-import-input").click()}
                    />
                  </Menu>
                }
                position={Position.BOTTOM_LEFT}
              >
                <Button icon="more" rightIcon="caret-down">
                  {t("templates.more_actions") || "More Actions"}
                </Button>
              </Popover>
              <input
                id="template-import-input"
                type="file"
                accept=".json"
                style={{ display: "none" }}
                onChange={handleImport}
              />
            </div>
          </>
        )}

        {isEditing && editingTemplate && (
          <Card className="template-edit-card">
            <H5>{t("templates.edit_template") || "Edit Template"}</H5>
            <div className="form-group">
              <label>{t("templates.name") || "Name"}:</label>
              <InputGroup
                value={editingTemplate.data.name}
                onChange={(e) =>
                  setEditingTemplate({
                    ...editingTemplate,
                    data: { ...editingTemplate.data, name: e.target.value },
                  })
                }
                placeholder={t("templates.name_placeholder") || "Enter template name..."}
              />
            </div>
            <div className="form-group">
              <label>{t("templates.description") || "Description"}:</label>
              <TextArea
                value={editingTemplate.data.description}
                onChange={(e) =>
                  setEditingTemplate({
                    ...editingTemplate,
                    data: { ...editingTemplate.data, description: e.target.value },
                  })
                }
                placeholder={t("templates.description_placeholder") || "Enter description..."}
                fill
                growVertically={false}
                rows={3}
              />
            </div>
            <div className="template-config-info">
              <p>
                <Icon icon="info-sign" /> {t("templates.config_saved") || "Configuration settings are saved automatically"}
              </p>
            </div>
            <div className="edit-actions">
              <Button onClick={() => setIsEditing(false)}>
                {t("common.cancel") || "Cancel"}
              </Button>
              <Button intent="primary" onClick={handleSaveEdit}>
                {t("common.save") || "Save"}
              </Button>
            </div>
          </Card>
        )}
      </div>
      {!isEditing && (
        <div className={Classes.DIALOG_FOOTER}>
          <div className={Classes.DIALOG_FOOTER_ACTIONS}>
            <Button onClick={onClose}>{t("common.close") || "Close"}</Button>
            <Button
              intent="primary"
              onClick={handleApplyTemplate}
              disabled={!selectedTemplateId}
            >
              {t("templates.apply") || "Apply Template"}
            </Button>
          </div>
        </div>
      )}
    </Dialog>
  );
};

TemplateManager.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  currentConfig: PropTypes.objectOf(PropTypes.any).isRequired,
  onApplyTemplate: PropTypes.func.isRequired,
};

export default TemplateManager;
