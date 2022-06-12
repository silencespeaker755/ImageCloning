import React, { useState, useRef, useEffect } from "react";
import { useQuery, useMutation } from "react-query";
import { useNavigate, useParams } from "react-router-dom";
import axios from "../setting";
import { Button } from "@material-ui/core";
import CropIcon from "@material-ui/icons/Crop";
import ReactLassoSelect, { getCanvas } from "react-lasso-select";
import Loading from "../components/Loading";

export default function CropPage() {
  const { backgroundId, imageId } = useParams();
  const [loading, setLoading] = useState(true);
  let navigate = useNavigate();

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
        console.log("success!");
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
      const msg = await axios.post("/crop", { image_id: imageId, points });
      return msg;
    },
    {
      retry: false,
      onSuccess: (msg) => {
        const { data } = msg;
        console.log("success!!");
        navigate(`/transform/${backgroundId}/${data}`);
      },
      onError: (err) => {},
    }
  );

  const handleSubmit = () => {
    uploadImage();
  };

  useEffect(() => {
    if (imageSize.height && imageSize.height !== "NaNpx") {
      setLoading(false);
    }
  }, [JSON.stringify(imageSize)]);

  return (
    <div className="border-section">
      <div className="flex-all-center">
        {isEventsLoading || loading ? (
          <Loading />
        ) : (
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
        )}
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
