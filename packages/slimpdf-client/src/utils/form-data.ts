/**
 * Cross-platform FormData utilities
 * Works in both browser and Node.js (18+)
 */

/**
 * File-like object that can be used with FormData
 */
export type FileInput = File | Blob;

/**
 * Create a FormData instance with a single file
 */
export function createFileFormData(
  fieldName: string,
  file: FileInput,
  filename?: string
): FormData {
  const formData = new FormData();

  // Use the filename from File object or fallback
  const name = filename || (file instanceof File ? file.name : 'file');
  formData.append(fieldName, file, name);

  return formData;
}

/**
 * Create a FormData instance with multiple files
 */
export function createMultiFileFormData(
  fieldName: string,
  files: FileInput[],
  filenames?: string[]
): FormData {
  const formData = new FormData();

  files.forEach((file, index) => {
    const name =
      filenames?.[index] ||
      (file instanceof File ? file.name : `file_${index}`);
    formData.append(fieldName, file, name);
  });

  return formData;
}

/**
 * Append additional form fields to FormData
 */
export function appendFormFields(
  formData: FormData,
  fields: Record<string, string | number | boolean | undefined>
): FormData {
  Object.entries(fields).forEach(([key, value]) => {
    if (value !== undefined) {
      formData.append(key, String(value));
    }
  });
  return formData;
}
