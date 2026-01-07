"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import axios from "axios";
import { useAuth } from "../../context/AuthContext";
import {
  MdLocationOn,
  MdBed,
  MdBathroom,
  MdSquareFoot,
  MdFavorite,
  MdFavoriteBorder,
  MdEmail,
  MdPhone,
  MdDelete,
} from "react-icons/md";

function PropertyDetailContent({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { user } = useAuth();
  const [property, setProperty] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [favorite, setFavorite] = useState(false);

  useEffect(() => {
    fetchProperty();
  }, [params.id]);

  const fetchProperty = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/listings/properties/${params.id}/`
      );
      setProperty(response.data);
      setFavorite(response.data.is_favorited || false);
    } catch (err: any) {
      console.error("Error fetching property:", err);
      setError("Failed to load property details");
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async () => {
    if (!user) {
      router.push("/login");
      return;
    }

    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        router.push("/login");
        return;
      }

      if (favorite) {
        await axios.delete(
          `${process.env.NEXT_PUBLIC_API_URL}/api/listings/favorites/${params.id}/`,
          { headers: { Authorization: `Token ${token}` } }
        );
        setFavorite(false);
      } else {
        await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/api/listings/favorites/`,
          { property: params.id },
          { headers: { Authorization: `Token ${token}` } }
        );
        setFavorite(true);
      }
    } catch (err: any) {
      console.error("Error toggling favorite:", err);
      alert(err.response?.data?.detail || "Failed to update favorite");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this property?")) return;

    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You must be logged in to delete properties");
        return;
      }

      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/api/listings/properties/${params.id}/`,
        { headers: { Authorization: `Token ${token}` } }
      );

      alert("Property deleted successfully");
      router.push("/properties");
    } catch (err: any) {
      console.error("Error deleting property:", err);
      alert(err.response?.data?.detail || "Failed to delete property");
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("en-ET", {
      style: "currency",
      currency: "ETB",
      maximumFractionDigits: 0,
    }).format(price);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || "Property not found"}</p>
          <Link href="/properties" className="text-blue-600 hover:underline mt-4 inline-block">
            Back to Properties
          </Link>
        </div>
      </div>
    );
  }

  const isOwner = user && property.owner && property.owner.id === user.id;

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center gap-3">
              <Image src="/logo.png" alt="Ereft" width={40} height={40} className="rounded-lg" />
              <span className="text-2xl font-bold text-black">Ereft</span>
            </Link>
            <nav className="hidden md:flex gap-6 items-center">
              <Link href="/properties" className="text-blue-600 font-semibold">Properties</Link>
              <Link href="/map" className="text-gray-700 hover:text-black">Map</Link>
              {user && (
                <Link href="/profile" className="text-gray-700 hover:text-black">Profile</Link>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Images Gallery */}
        <div className="mb-8">
          {property.images && property.images.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <div className="md:col-span-2 relative h-96 bg-gray-200 rounded-lg overflow-hidden">
                <Image
                  src={property.images[0].image}
                  alt={property.title}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="grid grid-cols-1 gap-2">
                {property.images.slice(1, 5).map((img: any, idx: number) => (
                  <div key={idx} className="relative h-48 bg-gray-200 rounded-lg overflow-hidden">
                    <Image src={img.image} alt={`${property.title} ${idx + 2}`} fill className="object-cover" />
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="relative h-96 bg-gray-200 rounded-lg overflow-hidden">
              <Image src="/logo.png" alt={property.title} fill className="object-contain" />
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Left Column - Main Info */}
          <div className="md:col-span-2">
            {/* Title and Badges */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-black mb-2">{property.title}</h1>
                <div className="flex items-center gap-2 text-gray-600 mb-4">
                  <MdLocationOn className="text-blue-600" />
                  <span>
                    {property.address}, {property.city}
                    {property.sub_city ? `, ${property.sub_city}` : ""}
                  </span>
                </div>
              </div>
              {isOwner && (
                <div className="flex gap-2">
                  <button
                    onClick={handleDelete}
                    className="p-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    title="Delete Property"
                  >
                    <MdDelete className="text-2xl" />
                  </button>
                </div>
              )}
            </div>

            {/* Badges */}
            <div className="flex gap-3 mb-6 flex-wrap">
              <span className="bg-blue-600 text-white text-sm px-3 py-1 rounded uppercase">
                {property.listing_type}
              </span>
              <span className="bg-gray-200 text-gray-700 text-sm px-3 py-1 rounded capitalize">
                {property.property_type}
              </span>
              {property.is_featured && (
                <span className="bg-yellow-500 text-white text-sm px-3 py-1 rounded">
                  Featured
                </span>
              )}
            </div>

            {/* Price */}
            <div className="mb-6">
              <p className="text-3xl sm:text-4xl font-bold text-blue-600 mb-2">{formatPrice(property.price)}</p>
              {property.price_per_sqm && (
                <p className="text-gray-600">
                  {formatPrice(property.price_per_sqm)} per m²
                </p>
              )}
            </div>

            {/* Description */}
            {property.description && (
              <div className="mb-8">
                <h2 className="text-xl sm:text-2xl font-bold mb-4 text-black">Description</h2>
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {property.description}
                </p>
              </div>
            )}

            {/* Property Details */}
            <div className="mb-8">
              <h2 className="text-xl sm:text-2xl font-bold mb-4 text-black">Property Details</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {property.bedrooms && (
                  <div className="bg-gray-50 rounded-lg p-4 text-center">
                    <MdBed className="text-3xl text-blue-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-black">{property.bedrooms}</p>
                    <p className="text-gray-600 text-sm">Bedrooms</p>
                  </div>
                )}
                {property.bathrooms && (
                  <div className="bg-gray-50 rounded-lg p-4 text-center">
                    <MdBathroom className="text-3xl text-blue-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-black">{property.bathrooms}</p>
                    <p className="text-gray-600 text-sm">Bathrooms</p>
                  </div>
                )}
                {property.area_sqm && (
                  <div className="bg-gray-50 rounded-lg p-4 text-center">
                    <MdSquareFoot className="text-3xl text-blue-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold text-black">{property.area_sqm}</p>
                    <p className="text-gray-600 text-sm">m²</p>
                  </div>
                )}
                {property.year_built && (
                  <div className="bg-gray-50 rounded-lg p-4 text-center">
                    <p className="text-3xl text-blue-600 font-bold mb-2">{property.year_built}</p>
                    <p className="text-gray-600 text-sm">Year Built</p>
                  </div>
                )}
              </div>
            </div>

            {/* Features */}
            {(property.has_garage || property.has_pool || property.has_garden || property.has_balcony || property.is_furnished || property.has_air_conditioning || property.has_heating) && (
              <div className="mb-8">
                <h2 className="text-xl sm:text-2xl font-bold mb-4 text-black">Features</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                  {property.has_garage && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Garage</span>
                    </div>
                  )}
                  {property.has_pool && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Pool</span>
                    </div>
                  )}
                  {property.has_garden && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Garden</span>
                    </div>
                  )}
                  {property.has_balcony && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Balcony</span>
                    </div>
                  )}
                  {property.is_furnished && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Furnished</span>
                    </div>
                  )}
                  {property.has_air_conditioning && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Air Conditioning</span>
                    </div>
                  )}
                  {property.has_heating && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Heating</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Contact/Info */}
          <div className="md:col-span-1">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 sticky top-24">
              <h3 className="text-xl font-bold mb-4 text-black">Contact</h3>
              {property.owner && (
                <>
                  <p className="text-gray-700 font-semibold mb-4">
                    {property.owner.first_name || property.owner.username}
                  </p>
                  <p className="text-sm text-gray-500 mb-3">Contact Listing Agent</p>
                  {property.owner.email && (
                    <a
                      href={`mailto:${property.owner.email}`}
                      className="flex items-center gap-3 text-gray-700 hover:text-blue-600 mb-3"
                    >
                      <MdEmail className="text-xl" />
                      <span className="text-sm break-all">{property.owner.email}</span>
                    </a>
                  )}
                  {property.owner.phone_number && (
                    <a
                      href={`tel:${property.owner.phone_number}`}
                      className="flex items-center gap-3 text-gray-700 hover:text-blue-600 mb-3"
                    >
                      <MdPhone className="text-xl" />
                      <span className="text-sm">{property.owner.phone_number}</span>
                    </a>
                  )}
                </>
              )}
              <button
                onClick={toggleFavorite}
                className="w-full flex items-center justify-center gap-2 bg-white border-2 border-blue-600 text-blue-600 rounded-lg px-4 py-3 hover:bg-blue-50 transition-colors font-semibold mb-4"
              >
                {favorite ? (
                  <>
                    <MdFavorite className="text-2xl text-red-500" />
                    <span>Remove from Favorites</span>
                  </>
                ) : (
                  <>
                    <MdFavoriteBorder className="text-2xl" />
                    <span>Add to Favorites</span>
                  </>
                )}
              </button>
              <Link
                href="/map"
                className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white rounded-lg px-4 py-3 hover:bg-blue-700 font-semibold"
              >
                View on Map
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function PropertyDetailPage({ params }: { params: { id: string } }) {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-white flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        </div>
      }
    >
      <PropertyDetailContent params={params} />
    </Suspense>
  );
}
