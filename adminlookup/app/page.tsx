'use client';

import { useState } from "react";
import axios from "axios";
import Head from "next/head";
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Download, Search } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function Home() {
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [adminData, setAdminData] = useState(null);
  const [availableLevels, setAvailableLevels] = useState([]);
  const [selectedLevel, setSelectedLevel] = useState('adm_1');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'https://admin-lookup-api.onrender.com'; 


  const handleLocate = async () => {
    setLoading(true);
    setError('');
    try {
        if (!latitude || !longitude) {
        setError("Please fill all fields before downloading/locating.");
        return;
      }
      const res = await axios.post(`${API_BASE}/locate`, {
        latitude : parseFloat(latitude),
        longitude: parseFloat(longitude)
      });
      setAdminData(res.data['Administrative Levels']);
      
    } catch (err) {
      setError('Could not fetch administrative data.')
      console.error(err)
    } finally {
      setLoading(false);
    }
  };

  const handlecheckLevels = async () => {
    setError('');

    try {
      const res = await axios.get(`${API_BASE}/available-levels`, {
        params: {latitude, longitude}
      });
      setAvailableLevels(res.data['available_levels'])
    } catch (err) {
      setError('Could not fetch administrative levels.')
      console.error(err)
    }
  };


  const handleDownload = async () => {
  setError('');
  try {
    if (!latitude || !longitude || !selectedLevel) {
  setError("Please fill all fields before downloading.");
  return;
}
    const url = `${API_BASE}/download?latitude=${latitude}&longitude=${longitude}&level=${selectedLevel}`;
    const response = await axios.get(url, {
      responseType: 'blob', // this is critical for binary streams
    });

    const blob = new Blob([response.data], { type: 'application/geo+json' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', `${selectedLevel}_${latitude}_${longitude}.geojson`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    setError('❌ Download failed.');
    console.error(err);
  }
};




  return (
    <>
    <Head>
      <title>Admin Lookup | East Africa</title>
    </Head>
    <main className="min-h-screen p-6 md:p-20 md:z-30 bg-gradient-to-br from-green-50 to-green-100 text-gray-800">
      <div className="max-w-xl mx-auto space-y-6">
        <h1 className="text-lg md:text-3xl font-bold text-center">East Africa Admin Lookup API</h1>
        <Card>
          <CardContent className="p-4 space-y-4 md:space-y-6 md:p-8">
            <TooltipProvider>
              <div className="flex gap-2">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Input
                      placeholder="Latitude"
                      value={latitude}
                      onChange={(e) => setLatitude(e.target.value)}
                      type="number"
                    />
                  </TooltipTrigger>
                  <TooltipContent>
                    Latitude goes from -12 (south) to 18 (north). Example: -1.29
                  </TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Input
                      placeholder="Longitude"
                      value={longitude}
                      onChange={(e) => setLongitude(e.target.value)}
                      type="number"
                    />
                  </TooltipTrigger>
                  <TooltipContent>
                    Longitude ranges from 28 to 52. Example: 36.82
                  </TooltipContent>
                </Tooltip>
              </div>
            </TooltipProvider>
            <div className="flex gap-2">
              <Button onClick={handleLocate} disabled={loading}>
                <Search className="mr-2 w-4 h-4" /> Locate
              </Button>
              <Button onClick={handlecheckLevels} variant="outline">
                Check Levels
              </Button>
            </div>
            {availableLevels.length > 0 && (
              <div className="space-y-1">
                <label htmlFor="level">Select Level:</label>
                <Tooltip>
                <TooltipTrigger asChild>
                  <select
                    id="level"
                    className="w-full border rounded p-2"
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                  >
                    {availableLevels.map((lvl) => (
                      <option key={lvl} value={lvl}>{lvl}</option>
                    ))}
                  </select>
                </TooltipTrigger>
                <TooltipContent>
                  Select the admin level you want. ADM_0 = country, ADM_1 = county, etc.
                </TooltipContent>
              </Tooltip>
              </div>
            )}
            <Button onClick={handleDownload} variant="secondary">
                <Download className="mr-2 w-4 h-4" /> Download GeoJSON
              </Button>
              {error && <p className="text-red-500 text-sm">{error}</p>}
              {adminData && (
                <div className="bg-white p-4 rounded shadow">
                  <h2 className="text-lg font-semibold mb-2">Administrative Info</h2>
                  <ul className="space-y-1">
                    {Object.entries(adminData).map(([key, value]) => (
                      <li key={key}><strong>{key}:</strong> {String(value)}</li>
                    ))}
                  </ul>
                </div>
              )}
          </CardContent>
        </Card>
      </div>
    </main>
    </>
  );
}
