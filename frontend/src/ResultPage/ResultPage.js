import React, { useState, useRef } from "react";
import { useQuery, useMutation } from "react-query";
import { useNavigate, useParams } from "react-router-dom";
import axios from "../setting";
import { Button } from "@material-ui/core";
import ReplayIcon from "@material-ui/icons/Replay";

export default function CropPage() {
  const { imageId } = useParams();
  const ref = useRef();
  let navigate = useNavigate();

  const [imageSize, setImageSize] = useState({
    height: 0,
    width: 0,
  });

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
      return url;
    },
    {
      retry: false,
      onSuccess: (data) => {
        console.log("success!");
      },
    }
  );

  const handleImageLoaded = () => {
    let height = ref.current.naturalHeight;
    let width = ref.current.naturalWidth;
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

  return (
    <div className="border-section">
      <div className="flex-all-center">
        <img
          ref={ref}
          src={image}
          alt="result"
          onLoad={handleImageLoaded}
          style={
            image ? { height: imageSize.height, width: imageSize.width } : {}
          }
        />
      </div>
      <div className="flex-all-center" style={{ marginTop: "30px" }}>
        <Button
          variant="outlined"
          startIcon={<ReplayIcon />}
          onClick={() => navigate("/")}
        >
          Back to Menu
        </Button>
      </div>
    </div>
  );
}
