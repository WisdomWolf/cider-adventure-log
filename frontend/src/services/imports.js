import axios from "../axios";

export async function previewImport(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await axios.post("/api/imports/preview", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function commitImport(beverages, nameMap) {
  const response = await axios.post("/api/imports/commit", {
    beverages,
    name_map: nameMap,
  });
  return response.data;
}
