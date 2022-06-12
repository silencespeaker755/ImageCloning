import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import HomePage from "./HomePage/HomePage";
import UploadPage from "./UploadPage/UploadPage";
import CropPage from "./CropPage/CropPage";
import TransformPage from "./TransformPage/TransformPage";
import ResultPage from "./ResultPage/ResultPage";

export default function App() {
  useEffect(() => {
    document.title = `ホームページ`;
  });

  return (
    <div>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/crop">
          <Route path=":backgroundId">
            <Route path=":imageId" element={<CropPage />} />
          </Route>
        </Route>
        <Route path="/transform">
          <Route path=":backgroundId">
            <Route path=":imageId" element={<TransformPage />} />
          </Route>
        </Route>
        <Route path="result">
          <Route path=":imageId" element={<ResultPage />} />
        </Route>
      </Routes>
    </div>
  );
}
