import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import UploadPage from "./UploadPage";
import CropPage from "./CropPage/CropPage";

export default function App() {
  useEffect(() => {
    document.title = `ホームページ`;
  });

  return (
    <div>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/crop">
          <Route path=":imageId" element={<CropPage />} />
        </Route>
      </Routes>
    </div>
  );
}
