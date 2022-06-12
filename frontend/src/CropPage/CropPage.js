import React, { useState, useRef } from "react";
import { useQuery, useMutation } from "react-query";
import { useParams } from "react-router-dom";
import axios from "../setting";
import { Button } from "@material-ui/core";
import CropIcon from "@material-ui/icons/Crop";
import ReactLassoSelect, { getCanvas } from "react-lasso-select";

export default function CropPage() {
  const { imageId } = useParams();
  const ref = useRef();

  const [imageSize, setImageSize] = useState({
    height: 0,
    width: 0,
  });
  const [points, setPoints] = useState([]);

  const {
    data: image = "",
    isError: isEventsError,
    isLoading: isEventsLoading,
    isFetching: isEventsFetching,
    refetch: refetchEvents,
  } = useQuery(
    "CroppedImageFetching",
    async () => {
      const data = await axios.get("/image", {
        params: { image_id: imageId },
        responseType: "blob",
      });
      console.log(data.data);
      let url = URL.createObjectURL(data.data);
      const img = new Image();
      img.src = url;
      img.onload = () => handleImageLoaded(img.height, img.width);
      return url;
    },
    {
      retry: false,
      onSuccess: (data) => {
        console.log(data);
      },
    }
  );

  const handleImageLoaded = (imageHeight, imageWidth) => {
    let height = imageHeight;
    let width = imageWidth;
    const maximum = 700;
    if (height > width) {
      width = (width * maximum) / height;
      height = maximum;
    } else {
      height = (height * maximum) / width;
      width = maximum;
    }
    setImageSize({
      height: `${height}px`,
      width: `${width}px`,
    });
  };

  const { mutate: uploadImage } = useMutation(
    async () => {
      console.log(points);
      const msg = await axios.post("/crop", { image_id: imageId, points });
      return msg;
    },
    {
      retry: false,
      onSuccess: (msg) => {
        const { data } = msg;
        console.log("success!!");
      },
      onError: (err) => {},
    }
  );

  const handleSubmit = () => {
    uploadImage();
  };

  return (
    <div className="border-section">
      <div className="flex-all-center">
        <ReactLassoSelect
          value={points}
          src={image}
          onChange={(value) => {
            setPoints(value);
            console.log(value);
          }}
          onComplete={(value) => {
            if (!value.length) return;
          }}
          onImageLoad={handleImageLoaded}
          imageStyle={
            image ? { height: imageSize.height, width: imageSize.width } : {}
          }
        />
        {/* <img
          ref={ref}
          src={image}
          alt="haha"
            onLoad={handleImageLoaded}
          style={
            image ? { height: imageSize.height, width: imageSize.width } : {}
          }
        /> */}
      </div>
      <div className="flex-all-center" style={{ marginTop: "30px" }}>
        <Button
          variant="outlined"
          startIcon={<CropIcon />}
          onClick={handleSubmit}
        >
          Crop
        </Button>
      </div>
    </div>
  );
}
