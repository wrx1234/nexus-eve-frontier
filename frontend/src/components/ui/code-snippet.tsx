import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { CheckIcon, CopyIcon } from "lucide-react";

interface CopyButtonProps {
  value: string;
}

export function CopyButton({ value }: CopyButtonProps) {
  const [hasCopied, setHasCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setHasCopied(true);
      setTimeout(() => setHasCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <Button variant="ghost" size="icon" onClick={copyToClipboard}>
      {hasCopied ? (
        <CheckIcon className="h-4 w-4" color="green" />
      ) : (
        <CopyIcon className="h-4 w-4" />
      )}
      <span className="sr-only">Copy code</span>
    </Button>
  );
}

export const CodeSnippet = ({ value = "https://t.me/SuiJarvisBot" }: { value?: string }) => {
  return (
    <div className="relative max-w-md mx-auto">
      <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border rounded-t-lg">
        <div className="flex space-x-2">
          <div className="h-3 w-3 rounded-full bg-red-500"></div>
          <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
          <div className="h-3 w-3 rounded-full bg-green-500"></div>
        </div>
        <CopyButton value={value} />
      </div>
      <pre className="p-4 rounded-b-lg bg-muted border-x border-b overflow-x-auto font-mono">
        <code className="text-sm font-mono">
          {value}
        </code>
      </pre>
    </div>
  );
};