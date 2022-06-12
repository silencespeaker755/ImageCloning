import React, { useState, useRef, useEffect } from "react";
import { useMutation } from "react-query";
import axios from "../setting";
import { Typography } from "@material-ui/core";
import AddPhotoAlternateIcon from "@material-ui/icons/AddPhotoAlternate";
import "../css/flex-style.css";

export default function InputPhotoSection({
  label,
  title,
  setId,
  submitting,
  reset,
}) {
  const [image, setImage] = useState(null);
  const ref = useRef();
  const [imageURL, setImageURL] = useState(null);
  const [imageSize, setImageSize] = useState({
    height: 0,
    width: 0,
  });

  const { mutate: uploadImage } = useMutation(
    async () => {
      const formData = new FormData();
      formData.append("image", image);
      const msg = await axios.post("/upload-image", formData);
      return msg;
    },
    {
      retry: false,
      onSuccess: (msg) => {
        const { data } = msg;
        console.log("success!!");
        setId(String(data));
        reset();
      },
      onError: (err) => reset(),
    }
  );

  useEffect(() => {
    if (submitting) {
      uploadImage();
    }
  }, [submitting]);

  const handleImageUpload = (e) => {
    if (e.target.files[0] !== null) {
      setImage(e.target.files[0]);
      setImageURL(URL.createObjectURL(e.target.files[0]));
    }
  };

  const handleImageLoaded = () => {
    console.log(ref);
    let height = ref.current.naturalHeight;
    let width = ref.current.naturalWidth;
    console.log(height, width);
    if (height > width) {
      width = (width * 300) / height;
      height = 300;
    } else {
      height = (height * 300) / width;
      width = 300;
    }
    setImageSize({
      height: `${height}px`,
      width: `${width}px`,
    });
  };

  return (
    <div style={{ width: "40%" }}>
      <div className="flex-all-center" style={{ marginBottom: "10px" }}>
        <Typography variant="h5" component="h2">
          {title}
        </Typography>
      </div>
      <div className="input-photo-block">
        <label htmlFor={label}>
          <input
            accept="image/*"
            style={{ display: "none" }}
            id={label}
            type="file"
            onChange={handleImageUpload}
          />
          <div
            className="flex-all-center height-100 width-100 mouse-cursor"
            style={{ minHeight: "300px", minWidth: "300px" }}
          >
            <div role="button" tabIndex="0">
              {imageURL ? (
                <img
                  src={imageURL}
                  ref={ref}
                  alt={`input-${imageURL}`}
                  style={
                    imageURL
                      ? { height: imageSize.height, width: imageSize.width }
                      : {}
                  }
                  onLoad={handleImageLoaded}
                />
              ) : (
                <AddPhotoAlternateIcon style={{ fontSize: 100 }} />
              )}
            </div>
          </div>
        </label>
      </div>
    </div>
  );
}
